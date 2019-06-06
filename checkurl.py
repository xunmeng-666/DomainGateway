import requests
import os
import time

class Object(object):
    def __init__(self):
        self.session = requests.session()
        self.url = {}

    def get_field(self):
        field_list = admin_class.model.objects.values()
        self.join_url(field_list)

    def join_url(self,list):
        self.url['host'] = []
        for field in list:
            if field['http'] == 0:
                http = 'http'
            else:
                http = 'https'
            host = field['ip']
            port = field['dport']
            domain = field['domain']
            url = "%s://%s:%s" %(http,host,port)
            self.url['host'].append({'id':field['id'],'http':http,'host':host,'port':port,'domain':domain,'url':url})

    def checkc_url(self):
        for url in self.url['host']:
            try:
                status_code = self.session.head(url['url']).status_code
                url['status_code'] = status_code
            except requests.ConnectionError:
                status_code = 504
                url['status_code'] = status_code

    def save_code(self):
        for code in self.url['host']:
            if AssetCheck.objects.filter(asset_id=code['id']):
                as_id = AssetCheck.objects.filter(asset_id=code['id']).values('id')[0]['id']
                AssetCheck.objects.filter(id=as_id).update(asset_id=int(code['id']),status_code=int(code['status_code']))
            else:
                AssetCheck.objects.create(asset_id=int(code['id']),status_code=int(code['status_code']))

    def main(self):

        self.get_field()
        self.checkc_url()
        self.save_code()


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateway.settings")
    import django
    django.setup()
    from asset.models import Asset,AssetCheck
    admin_class = Asset.objects.all()
    while True:
        time.sleep(300)
        Object().main()