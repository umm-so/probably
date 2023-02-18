import base64

import requests
from requests.utils import requote_uri


VERBOSE_SETTING = 1
BEEP = True

COMMON_PICTURE_EXTS = 'jpg,jpeg,png,gif,svg,webp,ico,bmp,tiff,psd'
COMMON_VIDEO_EXTS = 'mp4,mov,avi,flv,mkv,wmv,webm,swf,m3u8,m4a,m4v,mpg,mpeg'
COMMON_AUDIO_EXTS = 'mp3,wav,ogg,flac,aac'
COMMON_DOCUMENT_EXTS = 'pdf,doc,docx,xls,xlsx,ppt,pptx,odt,ods,odp,odg,odf,txt,rtf,md,xml'
COMMON_ARCHIVE_EXTS = 'zip,rar,tar,gz,bz2,7z'
COMMON_EXECUTABLE_EXTS = 'exe,msi,dll,so,bin,deb,rpm,jar,apk,ipa,appx'
COMMON_SCRIPT_EXTS = 'sh,ps1,py,rb,pl'
COMMON_WEB_EXTS = 'sha256,br,map,js,d,ts,tsx,jsx,html,htm,css,scss,less,php,asp,aspx,jsp,jspx,cshtml,ashx,ftlh,ftl,vm,erb,goht'
COMMON_SOURCE_EXTS = 'c,cpp,cs,go,java,py,rb,rs,swift,vb'
COMMON_DATABASE_EXTS = 'db,sql,sqlite,sqlite3'
COMMON_BACKUP_EXTS = 'bak,old,backup,bkp'
COMMON_CONFIG_EXTS = 'conf,cfg,ini,json,yaml,yml,env,config'
COMMON_EMAIL_EXTS = 'eml,emlx,mbox,msg'
COMMON_KEY_EXTS = 'pem,key,cer,crt,der,pfx,p12,csr'


# api ref: https://buckets.grayhatwarfare.com/docs/api/v1
def build_request(token: str, keyword: str, is_regex: bool, exts: str, exclude_exts: str, last_modified_after: int, batch: int) -> str:
    url = 'https://buckets.grayhatwarfare.com/api/v1/files'
    if is_regex:
        keyword = base64.b64encode(keyword.encode('utf-8')).decode('utf-8')
    if batch == -1:
        req = f'{url}/{keyword}/1/1'
    else:
        req = f'{url}/{keyword}/{batch*1000}/1000'

    req = req + f'?access_token={token}'
    if len(exts):
        req = req + f'&extensions={exts}'
    elif len(exclude_exts):
        req = req + f'&stopextensions={exclude_exts}'
    if last_modified_after != -1:
        req = req + f'&last-modified-from={last_modified_after}'
    if is_regex:
        req = req + f'&regexp=1'

    p(req, 2)
    return req


def p(arg: object, verbosity: int = 1) -> None:
    if verbosity <= VERBOSE_SETTING:
        print(arg)


def main():
    token = ''
    last_modified_after = 1666569600  # after 2022-10-24

    keyword = '.*.*'
    is_regex = True

    exts = ','.join([
        # COMMON_CONFIG_EXTS
        'env'
    ])

    exclude_exts = ','.join([
        COMMON_PICTURE_EXTS,
        COMMON_VIDEO_EXTS,
        COMMON_AUDIO_EXTS,
        COMMON_EXECUTABLE_EXTS,
        COMMON_WEB_EXTS
    ])

    all_domains = set()

    p(f'Fetching results for {keyword}...')
    url = build_request(token, keyword, is_regex, exts, exclude_exts, last_modified_after, -1)
    resp = requests.get(url).json()
    p(f'Found {resp["results"]} results')
    for i in range(int(resp['results']/1000)+1):
        p(f'Batch: {i*1000} - {min((i+1)*1000-1,resp["results"])} / {resp["results"]}')
        domains = {}
        url = build_request(token, keyword, is_regex, exts, exclude_exts, last_modified_after, i)
        resp = requests.get(url).json()
        if 'files' not in resp:
            p(resp)
        for file in resp['files']:
            if file['bucket'] in all_domains:
                continue
            all_domains.add(file['bucket'])
            domains.update({file['bucket']: file['url']})

        for url in domains.values():
            print(requote_uri(url).replace("'", "%27").replace('(', '%28').replace(')', "%29").replace('[', '%5B').replace(']', '%5D'))
        if BEEP and len(domains) > 0:
            print('\a')


if __name__ == '__main__':
    main()
