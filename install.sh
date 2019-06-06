#!/bin/bash

export dir=$pwd
install_python(){
	echo "Check Python version 3.x"
	which python3
	if [[ $? -ne 0 ]]; then
		#statements
		echo "Python3 not found"
		sleep 3
		echo "Install python3"
		yum install -y $(cat $dir/yum-requirements)
	else
		echo "Python3 existence"
	fi
}

update_pip(){
	echo "Update PIP "
	pip3 install  -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com --upgrade pip
	pip3 install  -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r requirements
}

sync_db(){
	echo "Create DB"
	python3 manage.py makemigrations
	python3 manage.py migrate
}

createuser(){
	cd $dir
	echo "Create Super User"
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin_pass')" | python manage.py shell
	echo "User create success"
}

start_service(){
	sh services.sh start
}

install_python
update_pip
sync_db
createuser
start_service
