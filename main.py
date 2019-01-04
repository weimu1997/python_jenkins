#!/usr/bin/env python
import jenkins,time,sys,requests

server = jenkins.Jenkins("url", username="admin", password="")
job_group = server.get_all_jobs()
first_loop = True
parameter_dict = {}

while True:
    try:
        if first_loop == True:
            print("=======================")
            print("## 任务列表如下: ")
            for list_num,list_value in enumerate(job_group):
                print("%02d) %s" % (list_num+1,job_group[list_num]["name"]))
            job_select = input("## 输入 数字 选择任务: ").strip()
            if job_select == "q":
                sys.exit(0)
            try:
                job_selectnum = int(job_select)
            except ValueError:
                continue
            if job_selectnum > len(job_group):
                continue
            job_name = job_group[job_selectnum-1]["name"]
            job_lastbuildnum = server.get_job_info(job_name)["nextBuildNumber"]
            first_loop = False
        print("=======================")
        print("## 当前准备执行的任务: " + job_name)
        job_property = server.get_job_info(job_name)["property"]
        if len(job_property) == 1:
            run_sure = input("## 该任务不需要参数，输入 y 确认执行，b 重新选择任务: ")
            if run_sure == "y":
                server.build_job(job_name)
            elif run_sure == "b":
                first_loop = True
                continue
            else:
                first_loop = True
                continue
        elif len(job_property) == 2:
            job_parameter = job_property[1]["parameterDefinitions"]
            for parameter_num in range(len(job_parameter)):
                parameter_dict_key = input("## 请输入对应的参数 " + job_parameter[parameter_num]["name"] + job_parameter[parameter_num]["description"])
                parameter_dict[job_parameter[parameter_num]["name"]] = parameter_dict_key
            print("## 确认参数:",end="",flush=True)
            for key,value in parameter_dict.items():
                print(" %s ==> %s  " % (key,value),end="",flush=True)
            print("")
            job_sure = input("## 输入 y 确认执行，n 重新输入参数，b 重新选择任务: ")
            if job_sure == "y":
                server.build_job(job_name,parameter_dict)
            elif job_sure == "n":
                parameter_dict.clear()
                continue
            elif job_sure == "b":
                parameter_dict.clear()
                first_loop = True
                continue
            else:
                parameter_dict.clear()
                first_loop = True
                continue
        print("=======================")
        print("## 等待服务端响应中 ",end="",flush=True)
        time.sleep(1)
        for i in range(5):
            print(".",end="",flush=True)
            time.sleep(2)
        print("",flush=True)
        time.sleep(1)
        print("## 打印服务端响应: ")
        time.sleep(1)
        print("=======================")
        time.sleep(1)
        job_buildoutput = server.get_build_console_output(job_name,job_lastbuildnum)
        print(job_buildoutput)
        job_buildresult = server.get_build_info(job_name,job_lastbuildnum)["result"]
        print("=======================")
        if job_buildresult == "SUCCESS":
            job_continue_whensuccess = input("## 执行成功！输入 y 继续执行任务，q 退出脚本: ")
            if job_continue_whensuccess == "y":
                parameter_dict.clear()
                first_loop = True
                continue
            else:
                sys.exit(0)
        elif job_buildresult != "SUCCESS":
            print("## 执行失败！联系运维进行处理！ ")
            job_continue_whenfail = input("## 输入 y 继续执行任务，q 退出脚本: ")
            if job_continue_whenfail == "y":
                parameter_dict.clear()
                first_loop = True
                continue
            else:
                sys.exit(0)
    except (KeyboardInterrupt,EOFError):
        print("")
        parameter_dict.clear()
        first_loop = True
        continue
    except (requests.exceptions.ConnectionError):
        print("")
        print("## 服务端失去响应，需重跑任务")
        parameter_dict.clear()
        first_loop = True
        continue
