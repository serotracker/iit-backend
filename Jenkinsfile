pipeline {
  agent { 
    docker { 
      image 'python:3.7.2' 
      args '''
        -e PATH="$PATH:${env.WORKSPACE}/.local/bin"
      '''
    } 
  }
  environment {
    FLASK_ENV = 'test'
    AIRTABLE_API_KEY = credentials('airtable_api_key')
    AIRTABLE_BASE_ID = credentials('airtable_base_id')
  } 
  stages {
    stage('Test') {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'pip install -r requirements.txt --user'
          echo $PATH
          echo "${env.WORKSPACE}"
          //sh 'python manage.py test'
        }
      }
    }
  }
}
