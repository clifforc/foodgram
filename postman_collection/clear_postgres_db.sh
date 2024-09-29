#!/bin/bash

DOCKER_COMPOSE_DIR=$(find ../ -name "docker-compose.yml" -not -path "*/env" -not -path "*/venv" -exec dirname {} \;)

if [ -z "$DOCKER_COMPOSE_DIR" ]; then
    echo "Не удалось найти файл docker-compose.yml"
    exit 1
fi

cd "$DOCKER_COMPOSE_DIR"
if [ $? -ne 0 ]; then
    echo "Не удалось перейти в директорию с docker-compose.yml"
    exit 1
fi

docker compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', \
'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', \
'TooLongFirstName', 'TooLongLastName', 'InvalidU\$ername', 'EmailInUse']
delete_num, _ = User.objects.filter(username__in=usernames_list).delete()
print(f"Удалено записей: {delete_num}")
exit(0)
EOF

status=$?
if [ $status -ne 0 ]; then
    echo "Произошла ошибка при выполнении команды в контейнере."
    exit $status
fi
echo "Операция завершена успешно."