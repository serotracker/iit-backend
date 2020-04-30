pipeline {
  agent { 
    docker { image 'python:3.7.2' } 
  }
  environment {
    FLASK_ENV = 'prod'
    AIRTABLE_API_KEY = credentials('airtable_api_key')
    AIRTABLE_BASE_ID = credentials('airtable_base_id')
  }  
  stages {
    stage('Build') {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'pip install -r requirements.txt --user'
          sh 'echo $FLASK_ENV'
          sh 'echo $AIRTABLE_API_KEY'
        }
      }
    }
  }
}

