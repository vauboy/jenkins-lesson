Для всех задач нужно будет сделать скриншоты, подтверждающие выполнение, за исключением изменений в Jenkinsfile, так как я их увижу в вашем репозитории. Скриншоты можно добавить в основные изменения во втором задании архивом.

# Задание 1. Настройка Jenkins
### 1. Развернуть контроллер Jenkins, произведя его базовую настройку.

Все скриншоты в архиве - https://github.com/AnMakar/jenkins-lesson/blob/homework_jenkins/jenkins.rar

Пробую развернуть Jenkins в докере согласно инструкции - https://www.jenkins.io/doc/book/installing/docker/#setup-wizard

`sudo docker network create jenkins`

`sudo docker run \
  --name jenkins-docker \
  --rm \
  --detach \
  --privileged \
  --network jenkins \
  --network-alias docker \
  --env DOCKER_TLS_CERTDIR=/certs \
  --volume jenkins-docker-certs:/certs/client \
  --volume jenkins-data:/var/jenkins_home \
  --publish 2376:2376 \
  docker:dind \
  --storage-driver overlay2`

Создаю dockerfile со следующим содержимым:

```
FROM jenkins/jenkins:2.332.2-jdk11
USER root
RUN apt-get update && apt-get install -y lsb-release
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt-get update && apt-get install -y docker-ce-cli
USER jenkins
RUN jenkins-plugin-cli --plugins "blueocean:1.25.3 docker-workflow:1.28"
```

`sudo docker build -t myjenkins-blueocean:2.332.2-1 .`

`sudo docker run \
  --name jenkins-blueocean \
  --rm \
  --detach \
  --network jenkins \
  --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client \
  --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 \
  --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  myjenkins-blueocean:2.332.2-1 `

Перехожу на страницу <Server-IP>:8080 в браузере.

`sudo docker exec jenkins-blueocean cat /var/jenkins_home/secrets/initialAdminPassword` - Получаю пароль администратора в выводе консоли и вбиваю его на открытой странице

Выбираю вариант с установкой плагинов из сообщества, всё устанавливается автоматически. Попадаю на страницу с созданием учетки первого администратора

### 2. Проверить наличие, а при отсутствии произвести установку следующих плагинов:
    - GitHub Branch Source Plugin
    - Matrix Authorization Strategy Plugin

Всё установлено по умолчанию

### 3. Создать пользователя developer и, используя Project-based Matrix Authorization Strategy, настроить ему права доступа для запуска новых билдов. Для пользователя, созданного на этапе начальной настройки предоставить полные права.

Статья по теме - https://www.tothenew.com/blog/jenkins-implementing-project-based-matrix-authorization-strategy/

### 4. Создать Pipeline и напиcать скрипт непосредственно в Jenkins, который будет выводить дату на контроллере Jenkins.

```
pipeline {
    agent any

    stages {
        stage('Вывод даты на контроллере Jenkins') {
            steps {
                sh "date"
            }
        }
    }
}
```

### 5. Предоставить доступ пользователю developer права для конфигурирования только для этого пайплайна (проекта) и, войдя под пользователем developer, заменить вывод даты на вывод версии bash на контроллере. Проверить работу пайплайна.

```
pipeline {
    agent any

    stages {
        stage('Вывод версии bash') {
            steps {
                sh "bash --version"
            }
        }
    }
}
```

### 6. Развернуть агент Jenkins, настроить подключение к нему через ssh и назначить ему метки unittest и build.

Пробую развернуть агент Jenkins в докере согласно инструкции - https://www.jenkins.io/doc/book/using/using-agents/

`ssh-keygen -f ~/.ssh/jenkins_agent_key`

Вставляю ключ в Jenkins

Мой публичный SSH ключ доступен комнадой `cat ~/.ssh/jenkins_agent_key.pub`

Дальше нужна команда следующего вида:
```
docker run -d --rm --name=agent1 -p 22:22 \
-e "JENKINS_AGENT_SSH_PUBKEY=[your-public-key]" \
jenkins/ssh-agent:alpine
```
Только меняю пункт [your-public-key] на результат вывода предыдущей команды

На этом этапе стало понятно, что Мастер Jenkins в докере никак не может увидеть Агент Jenkins в докере, какие бы настройки я не проводил (настраивал порты, переадресации, помещал в общую сеть, прописывал SSH ключи под разными пользователями - ничего не удавалось). Попробовал поставить Jenkins заново согласно инструкции для Linux (https://www.jenkins.io/doc/book/installing/linux/), а не Докер и всё заработало.

На агенте с помощью команды `sudo docker exec agent1 sh -c "which java"` узнал положение Java, иначе Jenkins Master никак не мог найти Java

### 7. Убрать все экзекьюторы с контроллера Jenkins.

Согласно терминологии (https://www.jenkins.io/doc/book/glossary/) 
>Executor
>A slot for execution of work defined by a Pipeline or Project on a Node. A Node may have zero or more Executors configured which corresponds to how many concurrent Projects or Pipelines are able to execute on that Node.

Чтобы понять что есть экзекьютор пришлось установить плагин Locale и поменять язык на английский - стало понятнее.
Выставил экзекьюторы на Мастере на ноль, но пайплайны не запускались на Агенте. Выставил на агенте опцию Usage на "Use this node as much as possible" и всё заработало на Агенте

# Задание 2. Jenkinsfile
### 1. Форкнуть репозиторий https://github.com/vauboy/jenkins-lesson.

Форкнутый репозиторий - https://github.com/AnMakar/jenkins-lesson
`git clone https://github.com/AnMakar/jenkins-lesson`
`cd jenkins-lesson/`
`git checkout feat1-add-jenkinsfile`

### 2. В ветке feat1-add-jenkinsfile находится Jenkinsfile, который нужно переписать с использованием декларативного синтаксиса. Сделать так, чтобы имена, создаваемых docker образов не пересекались в случае одновременного запуска билдов для разных веток.

Отредактировал Jenkinsfile
Заполнил информацию о себе в git
  
`git config --global user.email "antonimak1997@gmail.com"`

`git config --global user.name "AnMakar"`

`git commit -a -m "Изменил Jenkinsfile"`

`git push`

```
Username for 'https://github.com': AnMakar
Password for 'https://AnMakar@github.com':
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 6 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 333 bytes | 333.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To https://github.com/AnMakar/jenkins-lesson
   80a0553..cca9d2f  feat1-add-jenkinsfile -> feat1-add-jenkinsfile
```
  
### 3. Создать multi-branch pipeline с именем jenkins-lesson. В качестве источника добавить полученный после форка GitHub репозиторий из п.1. Настроить триггер для сканирование репозитория и установить периодичность в 1 минуту.

После настроек лог пайплайна пишет ошибку `ERROR: Error cloning remote repo 'origin'` - пока не смог её поправить
  
### 4. Создать Pull-Request для внесения изменений из feat1-add-jenkinsfile в main ветку, добавить vauboy ревьювером. Проверить, что в проекте jenkins-lesson в Jenkins появилась новая задача в Pull Requests

---

Полезные ссылки:
- [Установка Jenkins](https://www.jenkins.io/doc/book/installing/)
- [Использование агентов](https://www.jenkins.io/doc/book/using/using-agents/)
- [Синтаксис пайплайнов](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Шаги пайплайнов](https://www.jenkins.io/doc/pipeline/steps/)
- [Jenkinsfile](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Multibranch пайплайны](https://www.jenkins.io/doc/book/pipeline/multibranch/)
