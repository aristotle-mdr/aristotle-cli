import click
import json
import requests
import os

"""
I really wanted to call this parkes, after "Henry Parkes" Father of Federation.
"""

class FederaterV2(object):
    object_order = [
        # ('aristotle_mdr_links','relation'),
        ('aristotle_mdr','objectclass'),
        # ('aristotle_mdr','property'),
        # ('aristotle_mdr','conceptualdomain'),
        # ('aristotle_mdr','datatype'),
        # ('aristotle_mdr','valuedomain'),
        # ('aristotle_mdr','dataelementconcept'),
        # ('aristotle_mdr','dataelement'),
        # ('aristotle_dse','distribution'),
        # ('aristotle_dse','dataset'),
        # ('aristotle_dse','datasetspecification'),
        # ('comet','indicator'),
        # ('comet','indicatorset'),
        # ('mallard_qr','question'),
    ]

    def __init__(self, origin, destination, api_version, origin_user, origin_password, destination_user, destination_password):
        self.origin = {
            'url': origin.rstrip('/')+'/api/v2',
            'username': origin_user,
            'password': origin_password,
        }

        self.destination = {
            'url': destination.rstrip('/')+'/api/v3',
            'username': destination_user,
            'password': destination_password,
        }
        print(self.origin)
        print(self.destination)

    def federate(self):
        self.send_manifest()
        for obj_type in self.object_order:
            print("Requesting {} from {}".format(obj_type, self.origin))
            
            for obj in self.get_metadata_items_from_origin(obj_type):
                print(obj['uuid'])
                r = self.send_metadata_item_to_destination(obj)
                # print("About to send: ", f)
                # file_to_send = os.path.join(directory,f)
                # r = send_request(file_to_send, api, user, password)
                print("   -- Sent. Response", r.status_code, r.text)

    def send_manifest(self):
        print("Creating manifest")

        organisations = requests.get(
            self.origin['url']+'/organizations/',
            # auth=(self.origin['username'], self.origin['password']),
        )
        print("sdfsdf",organisations)
        organisations = organisations.json()

        registration_authorities = requests.get(
            self.origin['url']+'/ras/',
            # auth=(self.origin['username'], self.origin['password']),
        ).json()

        manifest = {
            "organizations": [
                {
                    "uuid": org['uuid'],
                    "name": org['name'],
                    "definition": org['definition'],
                    "namespaces": []
                }
                for org in organisations
            ],
            "registration_authorities": [
                {
                    "uuid": ra['uuid'],
                    "name": ra['name'],
                    "definition": ra['definition'],
                    "namespaces": []
                }
                for ra in registration_authorities
            ],
            "metadata": []
        }
        print("Sending manifest")
        # print(manifest)
        r= requests.post(
            self.destination['url']+'/metadata/',
            auth=(self.destination['username'], self.destination['password']),
            json=manifest
        )
        print(r)
        print(r.text)
        return r


    def send_metadata_item_to_destination(self, metadata):

        return requests.post(
            self.destination['url']+'/metadata/',
            auth=(self.destination['username'], self.destination['password']),
            json=metadata
        ) #, headers=headers)

    def get_metadata_items_from_origin(self, object_type): #args, endpoint, user, password):
        page = 1
        while True:
            print("Getting page", page)
            result = requests.get(
                self.origin['url']+'/metadata/',
                # auth=(self.origin['username'], self.origin['password']),
                params={"page":page, "type":"%s:%s"%object_type}
            )
            data = result.json()
            print(data)
            print("about to send {n} objects".format(n=len(data['results'])))
            for obj in data['results']:
                yield obj
            page += 1
            if not data['next']:
                break

@click.command()
@click.option('--origin', '-O', help='Origin registry')
@click.option('--destination', '-D', default='', help='Destination registry')
@click.option('--api_version', default=2, help='API version')
@click.option('--origin_user', default=None, help='API username')
@click.option('--origin_password', default=None, help='API password')
@click.option('--destination_user', default=None, help='API username')
@click.option('--destination_password', default=None, help='API password')
def command(origin, destination, api_version, origin_user, origin_password, destination_user, destination_password):
    """
    Send metadata from one registry to another.
    
    This is based on 
    """
    # r = send_request(manifest, api, user, password)
    # print(r.status_code, r.text)

    # response = requests.get(api)
    fed = FederaterV2(origin, destination, api_version, origin_user, origin_password, destination_user, destination_password)
    fed.federate()


if __name__ == "__main__":
    command()
