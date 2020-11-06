#!groovy

currentBuild.result = "SUCCESS"
String buildAgentLabel = "btcpro-build" //add your build agent name here
//noinspection GroovyUnusedAssignment
@Library('Pipeline-Global-Library') _

try {
    stage("Build") {
        node(buildAgentLabel) {
            envSetup()
            build()
        }
    }

    stage("Deploy") {
        node(buildAgentLabel) {
            deploy()
        }
    }


    stage("Promote") {
        node(buildAgentLabel) {
            promote()
        }
    }

}
catch (err) {
    echo err.toString()
    currentBuild.result = "FAILURE"
}

def envSetup(){
    deleteDir() //delete jenkins working dir for this project
    checkout scm //clones the git repository
}

def build() {
    //sh 'docker run -d -p 80:80 docker/getting-started'
    sh 'ls'
    sh 'docker-compose --version'
    sh 'docker-compose up -d   '
    sh 'python Mapping.py'
    sh 'python SaveIssues.py'
}

def staticAnalysis() {}

def unitTesting() {}

def deploy() {}

def functionalTesting() {}

def performanceTesting() {}

def promote() {}
