import logging
from json import loads, dumps
from time import time
from os import makedirs
from os.path import dirname
from os.path import join
from os.path import realpath
from zincjs_group_exporter import zinc_group
from zincjs_group_exporter.backend import Store, Job, Resource

db_src = 'sqlite://'

store = Store(db_src)
logger = logging.getLogger(__name__)

def export_threejs(inputs):
    myExport = zinc_group.PyZincExport()
    model = myExport.outputModel(inputs, [])
    job = Job()
    job.timestamp = int(time())
    for data in model:
        resource = Resource()
        resource.data = data
        job.resources.append(resource)

    response = loads(job.resources[0].data)
    store.add(job)
    for idx, obj in enumerate(response, 1):
        resource_id = job.resources[idx].id
        obj['URL'] = './scaffold/%d' % resource_id
    return response


def getZincJSModels(request):
    inputs = []
    ''' just a temporary workaround to get the file for demo purpose '''
    path = dirname(realpath(__file__))
    for k, values in request.args.items():
        if k == 'inputs':
            for v in values:
                filelocation = path + "/" + str(v)
                inputs.append(filelocation)

    export_inputs(inputs)


def export_threejs_cli(root, streams, annotations=None, subdir='scaffold'):
    if annotations is None:
        annotations = []

    output_dir = join(root, subdir)
    makedirs(output_dir)

    myExport = zinc_group.PyZincExport()
    model = myExport.outputModelFromStreams(streams, annotations)

    for idx, data in enumerate(model):
        if idx == 0:
            # manipulate the root node to include relative URI to
            # resource.
            root = loads(data)
            for ref, obj in enumerate(root, 1):
                obj['URL'] = './%d' % ref
            data = dumps(root)

        with open(join(output_dir, str(idx)), 'w') as fd:
            fd.write(data)


def main():
    import sys
    from os.path import isdir

    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        sys.stderr.write('Usage: %s <dir> [<model_file> ...]\n' % sys.argv[0])
        sys.stderr.write('\nIf model is absent, read a model from stdin.\n')
        sys.exit(1)

    if not isdir(sys.argv[1]):
        sys.stderr.write("'%s' is not a directory\n" % sys.argv[1])
        sys.exit(1)

    root = sys.argv[1]
    if len(sys.argv) == 2:
        files = [sys.stdin]
    else:
        files = [open(p, 'r') for p in sys.argv[2:]]

    export_threejs_cli(root, files)


if __name__ == '__main__':
    main()
