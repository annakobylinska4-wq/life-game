#!/bin/bash
# Deployment configuration for Life Game

# Build target: "local" for Mac testing, "aws" for AWS deployment
# - local: builds for your Mac's architecture (arm64 on Apple Silicon)
# - aws: builds for linux/amd64 (required for AWS Fargate)
BUILD_TARGET= "local" #"aws"

# Set Docker platform based on build target
if [ "$BUILD_TARGET" = "aws" ]; then
    export DOCKER_PLATFORM="linux/amd64"
else
    export DOCKER_PLATFORM=""
fi
