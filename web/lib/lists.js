/**
 * List functions to be exported from the design doc.
 */

var templates = require('kanso/templates');

exports.index = function (head, req) {
    start({code: 200, headers: {'Content-Type': 'text/html'}});

    var row, rows = [];
    while (row = getRow()) {
        rows.push(row);
    }

    var content = templates.render('index.html', req, {
        rows: rows
    });

    if (req.client) {
        $('#content').html(content);
        document.title = 'pytunia :: Overview';
    }
    else {
        return templates.render('base.html', req, {
            content: content,
            title: 'pytunia :: Overview'
        });
    }
};

exports.record = function (head, req) {
    start({code: 200, headers: {'Content-Type': 'text/html'}});

    var row, rows = [];
    var pass = true;
    var inprogress = false;
    var _id;

    // first row is record
    row = getRow();
    name = row.key[0];
    _id = row.value._id;
    description = row.value.description;

    // subsequent are associated tasks
    while (row = getRow()) {
        if (row.value.kwargs)
            if (row.value.kwargs.testname)
                row.value.name = row.value.kwargs.testname;
        if ('results' in row.value) {
            row['results_string'] = JSON.stringify(row.value.results, null, 1);
            if (!row.value.results.success)
                pass = false;
        }
        if (!row.value.completed)
            inprogress = true;
        rows.push(row);
    }

    var content = templates.render('record.html', req, {
        name: name,
        description: description,
        pass: pass,
        inprogress: inprogress,
        _id: _id,
        rows: rows
    });

    if (req.client) {
        $('#content').html(content);
        document.title = 'pytunia :: Overview';
    }
    else {
        return templates.render('base.html', req, {
            content: content,
            title: 'pytunia :: Overview'
        });
    }
};

exports.task = function (head, req) {
    start({code: 200, headers: {'Content-Type': 'text/html'}});

    var task_name = ''
    var row, rows = [];
    while (row = getRow()) {
        if (row.value.kwargs && row.value.kwargs.testname)
            task_name = row.value.kwargs.testname
        else
            task_name = row.value.name
        if ('results' in row.value)
            row['results_string'] = JSON.stringify(row.value.results, null, 1)
        rows.push(row);
    }
    var title = 'pytunia :: Task Detail: ' + task_name;

    var content = templates.render('task.html', req, {
        task_name: task_name,
        rows: rows
    });

    if (req.client) {
        $('#content').html(content);
        document.title = title;
    }
    else {
        return templates.render('base.html', req, {
            content: content,
            title: title
        });
    }
};
