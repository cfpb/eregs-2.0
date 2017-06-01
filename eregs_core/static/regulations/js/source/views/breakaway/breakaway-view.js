'use strict';
var $ = require( 'jquery' );
var _ = require( 'underscore' );
var Backbone = require( 'backbone' );
var SxS = require( './sxs-view' );
var Router = require( '../../router' );
var BreakawayEvents = require( '../../events/breakaway-events' );
var MainEvents = require( '../../events/main-events' );
var SidebarEvents = require( '../../events/sidebar-events' );
Backbone.$ = $;

var BreakawayView = Backbone.View.extend( {
  childViews: {},

  initialize: function() {
    this.externalEvents = BreakawayEvents;
    this.listenTo( this.externalEvents, 'sxs:open', this.openSxS );
  },

  openSxS: function( context ) {
        // context.url = context.regParagraph + '/' + context.docNumber + '?from_version=' + context.fromVersion;
    console.log( 'context: ', context );
    context.url = context.docNumber + '/' + context.regVersion + '/' + context.regParagraph;
    console.log( 'sxs url: ', context.url );

    this.childViews.sxs = new SxS( context );

    if ( Router.hasPushState ) {
      Router.navigate( 'sxs/' + context.url );
    }

    MainEvents.trigger( 'breakaway:open', _.bind( this.removeChild, this ) );
    SidebarEvents.trigger( 'breakaway:open' );
  },

  removeChild: function() {
    this.childViews.sxs.remove();
    delete this.childViews.sxs;
  }
} );

var breakaway = new BreakawayView();
module.exports = breakaway;
