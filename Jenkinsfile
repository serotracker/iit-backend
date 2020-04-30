pipeline {
  agent { 
    docker { image 'python:3.7.2' } 
  }
  environment {
    FLASK_ENV = 'prod'
    AIRTABLE_API_KEY = credentials('airtable_api_key')
    AIRTABLE_BASE_ID = credentials('airtable_base_id')
    //PATH = "/var/lib/jenkins/jobs/iit-backend/branches/ci-integration/workspace/.local/bin:$PATH"
  }  
  stages {
    stage('Build') {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'echo $PATH'
          sh 'pip install -r requirements.txt --user'
          sh 'python manage.py'
        }
      }
    }
  }
}

