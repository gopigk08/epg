import urllib.request
import json
import xml.etree.ElementTree as ET
import os

def main():
    base_url = "http://solapuristreams.iptv18.space/player_api.php?username=app&password=developer"
    xmltv_url = "http://solapuristreams.iptv18.space/xmltv.php?username=app&password=developer"

    print("Fetching Live Categories...")
    req = urllib.request.Request(f"{base_url}&action=get_live_categories")
    categories = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

    telugu_cat_id = None
    for cat in categories:
        if 'telugu' in cat.get('category_name', '').lower():
            telugu_cat_id = cat.get('category_id')
            print(f"Found Telugu category: {cat.get('category_name')} (ID: {telugu_cat_id})")
            break

    if not telugu_cat_id:
        print("Could not find a 'Telugu' category!")
        return

    print("\nFetching Live Streams in Telugu category...")
    req = urllib.request.Request(f"{base_url}&action=get_live_streams&category_id={telugu_cat_id}")
    streams = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

    telugu_epg_ids = set()
    for stream in streams:
        epg_id = stream.get('epg_channel_id')
        if epg_id:
            telugu_epg_ids.add(epg_id)

    print(f"Found {len(streams)} Telugu streams, with {len(telugu_epg_ids)} unique EPG IDs.")

    if not telugu_epg_ids:
        print("No EPG IDs found for Telugu channels.")
        return

    print("\nDownloading XMLTV File...")
    raw_epg_file = "xtream_epg_temp.xml"
    req = urllib.request.Request(xmltv_url, headers={'User-Agent': 'ExoPlayer'})
    with urllib.request.urlopen(req) as response, open(raw_epg_file, 'wb') as out_file:
        while True:
            chunk = response.read(8192 * 1024)
            if not chunk:
                break
            out_file.write(chunk)

    print("\nExtracting Telugu EPG data...")
    output_file = "Telugu_EPG.xml"

    filtered_channels = 0
    filtered_progs = 0

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write('<?xml version="1.0" encoding="utf-8"?>\n<tv>\n')
        
        context = ET.iterparse(raw_epg_file, events=('end',))
        for event, elem in context:
            if elem.tag == 'channel':
                ch_id = elem.get('id')
                if ch_id in telugu_epg_ids:
                    out.write(ET.tostring(elem, encoding='unicode'))
                    filtered_channels += 1
                elem.clear()
            elif elem.tag == 'programme':
                ch_id = elem.get('channel')
                if ch_id in telugu_epg_ids:
                    out.write(ET.tostring(elem, encoding='unicode'))
                    filtered_progs += 1
                elem.clear()
                
        out.write('</tv>\n')

    print(f"\n✅ Finished! Extracted {filtered_channels} channels and {filtered_progs} programmes.")
    print(f"Saved to {output_file}")

    if os.path.exists(raw_epg_file):
        os.remove(raw_epg_file)

if __name__ == "__main__":
    main()
