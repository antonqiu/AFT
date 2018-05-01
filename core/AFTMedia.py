import json
import os
import sys
from cement.utils import shell
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class AFTMedia:

    def __init__(self, log, options):
        self.out_dir = './analyzed/media'
        self.log = log
        self.options = options
        self.media_dir = options.media_dir
        if self.options.out_dir:
            self.out_dir = self.options.out_dir
            self.log.debug('out_dir is overwritten: %s' % self.options.out_dir, __name__)

    def geotag(self):
        if Path(self.out_dir).exists():
            print('Output directory exists. Files may be overwritten.')
            shell.Prompt("Press Enter To Continue", default='ENTER')
        else:
            Path(self.out_dir).mkdir(parents=True)

        if not Path(self.media_dir).exists():
            self.log.error('error: %s does not exist' % self.media_dir)
            sys.exit(1)
        elif not Path(self.media_dir).is_dir():
            self.log.error('error: %s it not a directory' % self.media_dir)
            sys.exit(1)

        lat_lng_list = []
        for root, subdirs, files in os.walk(self.media_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    with Image.open(file_path) as img:
                        thumb_path = os.path.join(self.out_dir, '%s.thumbnail' % filename.split('.')[0])
                        img.thumbnail((256, 256))
                        img.save(thumb_path, 'JPEG')
                        exif = {
                            TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in TAGS
                        }
                        if exif["GPSInfo"]:
                            gps_data = {}
                            for t in exif["GPSInfo"]:
                                sub_decoded = GPSTAGS.get(t, t)
                                gps_data[sub_decoded] = exif["GPSInfo"][t]
                            exif["GPSInfo"] = gps_data
                            lat_lng_list.append({
                                'gps': get_lat_lng(exif),
                                'file_path': os.path.abspath(thumb_path),
                                'datetime': get_if_exist(exif, 'DateTime'),
                                'datetime_original': get_if_exist(exif, 'DateTimeOriginal'),
                                'datetime_digitized': get_if_exist(exif, 'DateTimeDigitized'),
                            })
                except IOError:
                    continue
        features = build_feature_collection(lat_lng_list)
        with open(os.path.join(self.out_dir, "timeline.json"), "w") as write_file:
            json.dump(features, write_file)


def build_feature_collection(lat_lng_list):
    geo_json_list = {
        'type': 'FeatureCollection',
        'features': []
    }

    for point in lat_lng_list:
        datetime = None

        if point['datetime']:
            datetime = point['datetime']
        elif point['datetime_original']:
            datetime = point['datetime_original']
        elif point['datetime_digitized']:
            datetime = point['datetime_digitized']

        feature = {
            'type': 'Feature',
            'properties': {
                'file_path': point['file_path'],
                'datetime': datetime
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [point['gps'][1], point['gps'][0]]
            }
        }
        geo_json_list['features'].append(feature)

    return geo_json_list


# CREDIT: https://www.codingforentrepreneurs.com/blog/extract-gps-exif-images-python/

def get_if_exist(data, key):
    if key in data:
        return data[key]
    return None


def convert_to_degress(value):
    """Helper function to convert the GPS coordinates
    stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lng(exif):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lng = None
    exif_data = exif
    # print(exif_data)
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_latitude = get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = get_if_exist(gps_info, 'GPSLongitudeRef')
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat
            lng = convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lng = 0 - lng
    return lat, lng
