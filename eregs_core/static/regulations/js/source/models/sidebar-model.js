'use strict';
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');
var Helpers = require('../helpers');
var Resources = require('../resources');

Backbone.SidebarModel = MetaModel.extend({});

var sidebarModel = new Backbone.SidebarModel({
    supplementalPath: 'sidebar',

    getAJAXUrl: function(id) {
        var url,
            urlPrefix = window.APP_PREFIX;

        if (urlPrefix) {
            url = urlPrefix + 'sidebar/';
        }
        else {
            url = '/sidebar/';
        }

        if (id.indexOf('/') === -1) {
            url += Helpers.findVersion(Resources.versionElements);
            url += '/' + Helpers.findEffDate(Resources.versionElements);
        }
        url += '/' + id;

        console.log('target url: ' + url)
        return url;
    }

});

module.exports = sidebarModel;
