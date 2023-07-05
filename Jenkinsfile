#!/usr/bin/env groovy

@Library('jenkins-libraries')_

pipeline {
    agent {
        label 'jenkins-slave-docker'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr:'5'))
        timeout(time: 1, unit: 'HOURS')
    }
    environment {
        DISCORD_ID = "discord-hook-smashed"
        COMPOSE_FILE = "docker-compose-swarm.yml"
        REGISTRY_HOST = "registry.hosted-domains.com"

        BUILD_CAUSE = getBuildCause()
        VERSION = getVersion("${GIT_BRANCH}")
        GIT_ORG = getGitGroup("${GIT_URL}")
        GIT_REPO = getGitRepo("${GIT_URL}")

        BASE_NAME = "${GIT_ORG}-${GIT_REPO}"
        SERVICE_NAME = "${BASE_NAME}"
        CONFIG_NAME = "${BASE_NAME}"
    }
    stages {
        stage('Init') {
            steps {
                echo "\n--- Build Details ---\n" +
                        "JOB_NAME:      ${JOB_NAME}\n" +
                        "GIT_URL:       ${GIT_URL}\n" +
                        "BASE_NAME:     ${BASE_NAME}\n" +
                        "SERVICE_NAME:  ${SERVICE_NAME}\n" +
                        "CONFIG_NAME:   ${CONFIG_NAME}\n" +
                        "REGISTRY_HOST: ${REGISTRY_HOST}\n" +
                        "BUILD_CAUSE:   ${BUILD_CAUSE}\n" +
                        "GIT_BRANCH:    ${GIT_BRANCH}\n" +
                        "VERSION:       ${VERSION}\n"
                verifyBuild()
                sendDiscord("${DISCORD_ID}", "Pipeline Started by: ${BUILD_CAUSE}")
                getConfigs("${SERVICE_NAME}")   // use this to get service configs from deploy-configs
            }
        }
        stage('Dev Deploy') {
            when {
                allOf {
                    not { branch 'master' }
                }
            }
            environment {
                ENV_NAME = "dev"
                ENV_FILE = "service-configs/services/${SERVICE_NAME}/${ENV_NAME}.env"
                STACK_NAME = "${ENV_NAME}_${BASE_NAME}"
                TRAEFIK_HOST = "`dev.smwc.world`, `roms-dev.smwc.world`"
            }
            steps {
                echo "\n--- Starting ${ENV_NAME} Deploy ---\n" +
                        "STACK_NAME:    ${STACK_NAME}\n" +
                        "TRAEFIK_HOST:  ${TRAEFIK_HOST}\n" +
                        "ENV_FILE:      ${ENV_FILE}\n"
                sendDiscord("${DISCORD_ID}", "${ENV_NAME} Deploy Started")
                updateCompose("${COMPOSE_FILE}", "STACK_NAME", "${STACK_NAME}")
                stackPush("${COMPOSE_FILE}")
                stackDeploy("${COMPOSE_FILE}", "${STACK_NAME}")
                sendDiscord("${DISCORD_ID}", "${ENV_NAME} Deploy Finished")
            }
        }
        stage('Prod Deploy') {
            when {
                allOf {
                    branch 'master'
                    triggeredBy 'UserIdCause'
                }
            }
            environment {
                ENV_NAME = "prod"
                ENV_FILE = "service-configs/services/${SERVICE_NAME}/${ENV_NAME}.env"
                STACK_NAME = "${ENV_NAME}_${BASE_NAME}"
                TRAEFIK_HOST = "`smwc.world`, `roms.smwc.world`"
            }
            steps {
                echo "\n--- Starting ${ENV_NAME} Deploy ---\n" +
                        "STACK_NAME:    ${STACK_NAME}\n" +
                        "TRAEFIK_HOST:  ${TRAEFIK_HOST}\n" +
                        "ENV_FILE:      ${ENV_FILE}\n"
                sendDiscord("${DISCORD_ID}", "${ENV_NAME} Deploy Started")
                updateCompose("${COMPOSE_FILE}", "STACK_NAME", "${STACK_NAME}")
                stackPush("${COMPOSE_FILE}")
                stackDeploy("${COMPOSE_FILE}", "${STACK_NAME}")
                sendDiscord("${DISCORD_ID}", "${ENV_NAME} Deploy Finished")
            }
        }
    }
    post {
        always {
            cleanWs()
            script { if (!env.INVALID_BUILD) {
                sendDiscord("${DISCORD_ID}", "Pipeline Complete: ${currentBuild.currentResult}")
            } }
        }
    }
}
