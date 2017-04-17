#!/bin/sh



mail_robot()
{
    receivers="418622278@qq.com,286287737@qq.com"
    echo "$2" | mail -s "$1" ${receivers}
}

info()
{
    if [ $1 -ne 0 ]
    then
        mail_robot "database update failed"  "$2"
        return 1
    fi
}

fail_info()
{
    mail_robot "database update failed" "$1"
}


if [ $1 ]
then
    date=$1
else
    day=`date  +%w`
    if [ $day -eq 6 ]||[ $day -eq 0 ]
    then
	echo "weekend, no update"
	exit 0
    fi
    if [ $day -eq 1 ]
    then
	date=`date -d "3 days ago" +%Y%m%d`
    else
	date=`date -d "1 days ago" +%Y%m%d`
    fi
fi

echo ${date}

update_table(){
    ssh -p 8022 yingyang@61.130.4.98 'mysqldump -uyyzc -pyyzc_123 -h192.168.3.131 daily_data '$1' -w"TRADE_DT='${date}'" -t > /home/yingyang/.backups/'$1'.sql'
    if [ $? -ne 0 ]
    then
	fail_info $1" dump data faile"
	return 1
    fi
    scp -P 8022 yingyang@61.130.4.98:~/.backups/$1.sql .
    if grep -qc "INSERT" $1.sql
    then
        mysql -uyyzc -pyyzc_123 -h192.168.3.131 daily_data < $1.sql
	if [ $? -ne 0 ]
	then
	    fail_info $1" insert data faile"
	    return 1
	fi
    else
	fail_info $1" no data to insert"
	return 1
    fi
}

sum=0
for table in ashareeodprices ashareeodderivativeindicator
do
    update_table $table
    let sum=sum+$?
    rm -rf $table.sql
done

if [ $sum -eq 0 ]
then
  mail_robot "database update success" "finished"  
fi



