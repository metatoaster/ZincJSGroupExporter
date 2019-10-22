import logging
from json import loads, dumps
from time import time
from os.path import dirname
from os.path import join
from os.path import realpath
from pkg_resources import get_distribution
from sanic import Sanic
from sanic.response import json, html, text, redirect
from zincjs_group_exporter import zinc_group
from zincjs_group_exporter import backend

db_src = 'sqlite://'
app = Sanic()

with open(join(dirname(__file__), 'static', 'view.json')) as vd:
    view_json = loads(vd.read())
    
bundle_js = get_distribution('zincjs_group_exporter').get_metadata(
    'calmjs_artifacts/bundle.js')

store = backend.Store(db_src)
logger = logging.getLogger(__name__)

def build(inputs):
    myExport = zinc_group.PyZincExport()
    model = myExport.outputModel(inputs, [])
    job = backend.Job()
    job.timestamp = int(time())
    for data in model:
        resource = backend.Resource()
        resource.data = data
        job.resources.append(resource)
    response = loads(job.resources[0].data)
    store.add(job)
    for idx, obj in enumerate(response, 1):
        resource_id = job.resources[idx].id
        obj['URL'] = './output/%d' % resource_id
    return response
        

@app.route('/output/<resource_id:int>')
async def output(request, resource_id):
    return json(store.query_resource(resource_id))

@app.route('/getZincJSModels')
async def getZincJSModels(request):
    inputs = []
    ''' just a temporary workaround to get the file for demo purpose '''
    path = dirname(realpath(__file__))
    for k, values in request.args.items():
        if k == 'inputs':
            for v in values:
                filelocation = path + "/" + str(v)
                inputs.append(filelocation) 
    try:
        response = build(inputs)
    except Exception as e:
        logger.exception('error while outputting mesh')
        return json({'error': 'error outputting mesh: ' + str(e)}, status=400)
        
    return json(response)

@app.route('/zincjs_group_exporter.js')
async def serve_js(request):
    return text(bundle_js, headers={'Content-Type': 'application/javascript'})

@app.route('/static/view.json')
async def view(request):
    return json(view_json)

html_file = join(dirname(__file__), 'static', 'output.html')
app.static('/output.html', html_file)

js_file = join(dirname(__file__), 'static', 'physiomeportal.js')
app.static('/physiomeportal.js', js_file)

def main():
    app.run(host='0.0.0.0', port=7575)


if __name__ == '__main__':
    main()
