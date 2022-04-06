node('unittest'){

    stage('Checkout code'){
        checkout scm
    }

    def image = docker.build("unittests")

    parallel unittest: {
        stage('Run unittests'){
            image.inside() {
                sh "python3 -m pytest"
            }
        }
    }, linter: {
        stage('Run linter'){
            try{
                image.inside() {
                    sh "prospector -o pylint:report/pylint.log src/"
                }
            } catch (error) {
                throw error
            } finally {
                sh "cat report/pylint.log"
            }
        }
    }, failFast: true

    stage('Publish reports') {
        cobertura(
            onlyStable: false,
            enableNewApi: true,
            failUnhealthy: false,
            failUnstable: false,
            autoUpdateHealth: false,
            autoUpdateStability: false,
            zoomCoverageChart: false,
            maxNumberOfBuilds: 0,
            sourceEncoding: 'ASCII',
            coberturaReportFile: 'report/coverage.xml',
            lineCoverageTargets: '80, 0, 0',
            methodCoverageTargets: '80, 0, 0',
            conditionalCoverageTargets: '70, 0, 0'
        )
    }

    stage('Build'){
        image.inside(){
            sh 'python3 -m build'
        }
    }

    stage('Publish artifact') {
        archiveArtifacts artifacts: 'dist/*.whl', fingerprint: false
    }
}