from __future__ import print_function

import os, argparse, pickle, json, requests

parser = argparse.ArgumentParser()

parser.add_argument("query", type=str)
parser.add_argument("--n_images", type=int)
parser.add_argument("--save_path", type=str, default='output')

# can be [thumb, small, regular, full, raw]
parser.add_argument("--quality", type=str, default='raw')

args = parser.parse_args()


def create_url(query='face', per_page=30, page_num=1):
    url = "https://unsplash.com/napi/search/photos?"
    url += "query=" + query             # add search term 
    url += "&per_page=" + str(per_page) # 30 is the limit
    url += "&page=" + str(page_num)     # page number
    return url 

def get_results(url, field='results'):
    return json.loads(requests.get(url).text)[field]


# get max images for query
url = create_url(query=args.query, per_page=1, page_num=1)
n_max = get_results(url, field='total')
print(n_max, 'total images for the query', args.query)
if args.n_images > n_max:
    n_images = n_max
    print('Only', n_max, 'images found. ')
else:
    n_images = args.n_images

# get entire list of meta and urls in advance
print('Downloading meta for', n_images, 'images')
n_processed = 0
meta = []
curr_page = 1
while n_processed < n_images:
    url = create_url(query=args.query, page_num=curr_page)
    curr_page += 1
    results = get_results(url)
    n_processed += 30
    if n_processed > n_images:
        diff = n_processed - n_images
        meta.extend(results[:-diff])
    else:
        meta.extend(results)
print('Done...')

# create output directory if needed
if not os.path.exists(args.save_path):
    os.makedirs(args.save_path)
    print('Save path does not exist. Created.')

meta_out_fn = 'meta_'+args.query+'_'+str(n_images)+'.p'
meta_out_path = os.path.join(args.save_path, meta_out_fn)
pickle.dump(meta, open(meta_out_path, 'wb'))

im_path = os.path.join(args.save_path,'images')
if not os.path.exists(im_path):
    os.makedirs(im_path)
print('')

# download each image
for i, img_meta in enumerate(meta):
    im_url = img_meta['urls'][args.quality]
    try:
        response = requests.get(im_url)
        if response.status_code == 200:
            with open(os.path.join(im_path, str(i)+'.jpg'), 'wb') as f:
                f.write(response.content)
                f.close()
        print('Downloaded image', i)
    except:
        print('ERROR getting image', i)





#
