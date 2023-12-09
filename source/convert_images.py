#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import time

#prefix = 'https://intranetproxy.alipay.com/skylark'
prefix = 'https://cdn.nlark.com/yuque'
postfix = '#'
local_img_folder = 'assets/post_images/'
#md_path  = r'/Users/yan/Blog/GithubHexoBlog/source/_posts/'
md_path = r'/Users/yan/Documents/Projects/my-hexo-page/source/_posts/'
#local_img_prefix = r'/Users/yan/Blog/GithubHexoBlog/source/'
local_img_prefix = r'/Users/yan/Documents/Projects/my-hexo-page/source/'

def gen_image_name_from_idx(idx, img_folder_path, postfix = 'png'):
    if idx < 10:
        name = '00' + str(idx)
    elif idx < 100:
        name = '0' + str(idx)
    elif idx < 1000:
        name = str(idx)
    res = img_folder_path + '/image_' + name + '.' + postfix
    print('[gen image name] ' + res)
    return res


def handle_md_images(md_name):
    md_file_path = md_path + md_name + '.md'
    img_path_folder = local_img_folder + md_name
    if not os.path.exists(local_img_prefix + img_path_folder):
        print('[mkdir] : ' + local_img_prefix + img_path_folder)
        os.mkdir(local_img_prefix + img_path_folder)
    img_idx = 0
    try:
        if md_file_path.split('.')[-1] == 'md':
            split_file_name = md_file_path.split('.')
            split_file_name[-2] += '_converted'
            copy_md_file_path = '.'.join(split_file_name)
            write_lines = []
            img_idx = 0
            # 打开md文件然后进行替换
            with open(md_file_path, 'r', encoding='utf8') as fr:
                    lines = fr.readlines()
                    for line in lines:
                        _line = line          
                        if prefix in line:
                            search_from = 0
                            while search_from < len(line):
                                # find image ref url
                                start_idx = line.find(prefix,search_from)
                                end_idx = line.find(postfix, search_from)
                                if start_idx < 0 or end_idx < 0:
                                    break
                                img_url = line[start_idx:end_idx]
                                search_from = end_idx + 1
                                print(img_url)
                                
                                # download image
                                img_postfix = img_url.split('.')[-1]
                                local_img =  gen_image_name_from_idx(img_idx,img_path_folder,img_postfix)
                                img_idx += 1
                                local_img_path = local_img_prefix + local_img
                                print('[download img] from URL: {' + img_url+ '} to local path: {' + local_img + '}')
                                cmd_wget = 'wget -O ' + local_img_path + ' ' + img_url
                                print(cmd_wget)
                                os.system(cmd_wget)

                                # replace md content
                                _line = _line.replace(img_url,local_img,1)
                        write_lines.append(_line)

            with open(copy_md_file_path, 'w', encoding='utf8') as fw:
                    fw.writelines(write_lines)  # 新文件一次性写入原文件内容
                    # fw.flush()

            # 备份原文件
            os.rename(md_file_path, md_file_path + '.bak')
            # 重命名新文件名为原文件名
            os.rename(copy_md_file_path, md_file_path)
            print(f'{md_file_path} done...')
            time.sleep(0.5)
    except FileNotFoundError as e:
        print(e)

import sys
if __name__ == '__main__':

    if 1:
        if len(sys.argv) > 1 and sys.argv[1] != "":
            md_name = sys.argv[1]
        else:
            md_name = r'DS-VS-DL'
        handle_md_images(md_name)
    else:
        for file in os.listdir(md_path):
            if file.endswith('.md'):
                md_name = file.split('.')[:-1]
                handle_md_images('.'.join(md_name))