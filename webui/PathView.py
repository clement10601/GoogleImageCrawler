import os
import json
import re
import mimetypes
import stat

from flask.views import MethodView
from flask import request, make_response, render_template, send_file, Response
from werkzeug import secure_filename

class PathView(MethodView):
    root = ''
    ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg', '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX', 'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']

    def get(self, p=''):
        hide_dotfile = request.args.get('hide-dotfile', request.cookies.get('hide-dotfile', 'no'))

        path = os.path.join(self.root, p)
        if os.path.isdir(path):
            contents = []
            total = {'size': 0, 'dir': 0, 'file': 0}
            for filename in os.listdir(path):
                if filename in self.ignored:
                    continue
                if hide_dotfile == 'yes' and filename[0] == '.':
                    continue
                filepath = os.path.join(path, filename)
                stat_res = os.stat(filepath)
                info = {}
                info['name'] = filename
                info['mtime'] = stat_res.st_mtime
                ft = self.get_type(stat_res.st_mode)
                info['type'] = ft
                total[ft] += 1
                sz = stat_res.st_size
                info['size'] = sz
                total['size'] += sz
                contents.append(info)
            page = render_template('index.html', path=p, contents=contents, total=total, hide_dotfile=hide_dotfile)
            res = make_response(page, 200)
            res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
        elif os.path.isfile(path):
            if 'Range' in request.headers:
                start, end = self.get_range(request)
                res = self.partial_response(path, start, end)
            else:
                res = send_file(path)
                res.headers.add('Content-Disposition', 'attachment')
        else:
            res = make_response('Not found', 404)
        return res

    def post(self, p=''):
        path = os.path.join(self.root, p)
        info = {}
        if os.path.isdir(path):
            files = request.files.getlist('files[]')
            for file in files:
                try:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(path, filename))
                except Exception as e:
                    info['status'] = 'error'
                    info['msg'] = str(e)
                else:
                    info['status'] = 'success'
                    info['msg'] = 'File Saved'
        else:
            info['status'] = 'error'
            info['msg'] = 'Invalid Operation'
        res = make_response(json.JSONEncoder().encode(info), 200)
        res.headers.add('Content-type', 'application/json')
        return res

    def get_range(self, request):
        range = request.headers.get('Range')
        m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
        if m:
            start = m.group('start')
            end = m.group('end')
            start = int(start)
            if end is not None:
                end = int(end)
            return start, end
        else:
            return 0, None

    def partial_response(self, path, start, end=None):
        file_size = os.path.getsize(path)

        if end is None:
            end = file_size - start - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        with open(path, 'rb') as fd:
            fd.seek(start)
            bytes = fd.read(length)
        assert len(bytes) == length

        response = Response(
            bytes,
            206,
            mimetype=mimetypes.guess_type(path)[0],
            direct_passthrough=True,
        )
        response.headers.add(
            'Content-Range', 'bytes {0}-{1}/{2}'.format(
                start, end, file_size,
            ),
        )
        response.headers.add(
            'Accept-Ranges', 'bytes'
        )
        return response

    def get_type(self, mode):
        if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
            type = 'dir'
        else:
            type = 'file'
        return type