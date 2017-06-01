'use strict';
var _ = require( 'underscore' );
var Backbone = require( 'backbone' );
var MetaModel = require( './meta-model' );
var Helpers = require( '../helpers' );
var Resources = require( '../resources' );

Backbone.SidebarModel = MetaModel.extend( {} );

var sidebarModel = new Backbone.SidebarModel( {
  supplementalPath: 'sidebar'
} );

module.exports = sidebarModel;
