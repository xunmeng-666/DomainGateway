#!/bin/bash

gateway_dir=

base_dir=$(dirname $0)
gateway_dir=${gateway_dir:-$base_dir}
PROC_NAME="gateway"

start() {
        if [ $(whoami) != 'root' ];then
            echo "Sorry, GW must be run as root"
            exit 1
        fi
        ps aux|grep 'manage.py' |grep -v 'grep' &> /dev/null
        if [ $? == '0' ];then
            echo "服务已启动"
        else
            nohup python3 running.py &>> /var/log/gateway.log 2>&1
            if [ $? == '0' ];then
                echo "服务启动成功"
                echo
            else
                echo "服务启动失败"
                echo
            fi
        fi
}


stop() {
    echo -n $"Stopping ${PROC_NAME} service:"
    ps aux | grep -E 'manage.py' | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ]; then
        echo "服务停止成功"
        echo
    else
        echo "服务已停止"
        echo
    fi

}

status(){
    ps axu | grep 'manage.py' | grep -v 'grep' &> /dev/null
    if [ $? == '0' ];then
        echo -n "服务运行中..."
        echo
    else
        echo -n "服务未运行."
        echo
    fi
}



restart(){
    stop
    start
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;

  restart)
        restart
        ;;

  status)
        status
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac