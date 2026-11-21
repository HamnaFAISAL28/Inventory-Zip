@echo off
REM Local scan against SonarCloud. Set first:  set SONAR_TOKEN=your_token
python -m pytest
sonar-scanner -Dsonar.token=%SONAR_TOKEN%
