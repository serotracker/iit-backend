pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('Build') {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh "pip install -r requirements.txt --user"
        }
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
      }   
    }
  }
}

