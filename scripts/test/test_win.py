import argparse
import json
import os
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Main Entry for Test Script")
    parser.add_argument("--custom", type=bool, default=False, help="use custom configuration")
    parser.add_argument("--config", type=str, default="default", help="configuration file")
    args = parser.parse_args()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = ""
    if args.config == "default":
        # if no `config.json`, copy `_config_<platform>.json` to `config.json` as default test configuration
        default_config_file_path = os.path.join(current_dir, "config/builtin/_config_win.json")
        config_file_path = os.path.join(current_dir, "config.json")
        if not os.path.isfile(config_file_path):
            print(f"connot find default configuration from {config_file_path}")
            print(f"will copy the default configuration from {default_config_file_path}")
            subprocess.run(["powershell", "Copy-Item", default_config_file_path, config_file_path], shell=True)

    else:
        # set config file path
        if not args.custom:
            print(f"use builtin configuration, config: {args.config}")
            config_file_path = os.path.join(current_dir, f"config/builtin/{args.config}.json")
        else:
            print(f"use custom configuration, config: {args.config}")
            config_file_path = os.path.join(current_dir, f"config/custom/{args.config}.json")

    # read configuration from `config.json`

    config = {}
    with open(config_file_path) as f:
        config = json.load(f)
        f.close()

    # if get configuration successfully, run test

    if config != set():
        print("get configuration successfully")
        build_system = config["build_system"]
        device_list = config["device_list"]
        feat_list = config["feat_list"]
        if build_system == "cmake":
            print("get build system: cmake")
            print("start to run test")
            for feat in feat_list:
                print(f"test feature: {feat}")
                args = ["powershell", os.path.join(config["bin"], "test_all.exe"), "--build",  f"-ts={feat}"]
                for device in device_list:
                    args.append(f"--backend-{device}")
                print(f"run command: {args}")
                subprocess.run(args, shell=True)
        elif build_system == "xmake":
            print("get build system: xmake")
            print("start to run test")
            for feat in feat_list:
                print(f"test feature: {feat}")
                args = ["powershell", "xmake", "run", "test_all", f"-ts={feat}"]
                for device in device_list:
                    args.append(f"--backend-{device}")
                print(f"run command: {args}")
                subprocess.run(args, shell=True)
        print("all test finished")
    else:
        print("get configuration failed")
        exit(1)
