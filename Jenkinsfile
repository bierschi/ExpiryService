pipeline {
         agent any
         stages {
                 stage('Build Package') {
                     steps {
                         echo 'Build package ExpiryService'
                         sh 'pip3 install -r requirements.txt'
                     }
                 }
                 stage('Static Code Metrics') {

                    steps {
                        echo 'Test Coverage'

                        echo 'Style checks with pylint'
                        sh 'pylint3 --reports=y ExpiryService/ || exit 0'
                    }

                 }
                 stage('Unit Tests') {
                    steps {
                        echo 'Test package ExpiryService'
                        sh 'python3 -m unittest discover ExpiryService/test/ -v'
                    }
                 }
                 stage('Build Distribution Packages') {
                    when {
                         expression {
                             currentBuild.result == null || currentBuild.result == 'SUCCESS'
                         }
                    }
                    steps {
                        echo 'Build Source Distribution'
                        sh 'python3 setup.py sdist'

                        echo 'Build Wheel Distribution'
                        sh 'python3 setup.py bdist_wheel'
                    }
                    post {
                        always {
                              archiveArtifacts (allowEmptyArchive: true,
                              artifacts: 'dist/*whl', fingerprint: true)
                        }
                        success {
                            echo 'Install package ExpiryService'
                            sh 'sudo python3 setup.py install'
                        }
                    }
                 }
                 stage('Deploy/Install To Target Server') {
                    steps {
                        echo 'Deploy ExpiryService to target server'

                    }
                }


    }
}
