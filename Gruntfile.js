'use strict';

module.exports = function( grunt ) {

  grunt.initConfig( {

    /**
     * Pull in the package.json file so we can read its metadata.
     */
    pkg: grunt.file.readJSON( 'package.json' ),

    /**
     *
     *  Pull in environment-specific vars
     *
     */
    env: grunt.file.readJSON( 'config.json' ),

    /* copy any npm installed files that need a new home */
    copy: {
      main: {
        files: [
          {
            expand: true,
            flatten: true,
            src: [ 'node_modules/respond.js/dest/*' ],
            dest: '<%= env.frontEndPath %>/js/built/lib/respond/',
            filter: 'isFile'
          }
        ]
      }
    },

    /**
     * https://github.com/gruntjs/grunt-contrib-less
     */
    less: {
      dev: {
        options: {
          paths: [ '<%= env.frontEndSourcePath %>/css/less' ],
          compress: false,
          sourceMap: true,
          sourceMapFilename: '<%= env.frontEndPath %>/css/style.css.map',
          sourceMapBasepath: '<%= env.frontEndPath %>/css/less/',
          sourceMapURL: 'style.css.map'
        },
        files: {
          '<%= env.frontEndPath %>/css/style.css': '<%= env.frontEndSourcePath %>/css/less/main.less'
        }
      }
    },

    /**
     * CSSMin: https://github.com/gruntjs/grunt-contrib-cssmin
     *
     * Minify CSS for production
     */
    cssmin: {
      target: {
        files: {
          '<%= env.frontEndPath %>/css/regulations.min.css': [ '<%= env.frontEndSourcePath %>/css/style.css' ]
        }
      }
    },

    /**
     * ESLint: https://github.com/sindresorhus/grunt-eslint
     *
     * Validate files with ESLint.
     */
    eslint: {
      target: [
        'Gruntfile.js',
        '<%= env.frontEndSourcePath %>/js/source/*.js',
        '<%= env.frontEndSourcePath %>/js/source/events/**/*.js',
        '<%= env.frontEndSourcePath %>/js/source/models/**/*.js',
        '<%= env.frontEndSourcePath %>/js/source/views/**/*.js'
      ]
    },

    /**
    * Browserify:
    *
    * Require('modules') in the browser/bundle up dependencies.
    */
    browserify: {
      dev: {
        files: {
          '<%= env.frontEndPath %>/js/built/regulations.js': [ '<%= env.frontEndSourcePath %>/js/source/regulations.js',
            '<%= env.frontEndSourcePath %>/js/source/regulations.js' ]
        },
        options: {
          browserifyOptions: {
            debug: true
          }
        }
      },
      dist: {
        files: {
          '<%= env.frontEndPath %>/js/built/regulations.js': [ '<%= env.frontEndSourcePath %>/js/source/regulations.js' ]
        },
        options: {
          browserifyOptions: {
            debug: false
          }
        }
      }
    },

    uglify: {
      dist: {
        files: {
          '<%= env.frontEndPath %>/js/built/regulations.min.js': [ '<%= env.frontEndPath %>/js/built/regulations.js' ]
        }
      }
    },

    mocha_istanbul: {
      coverage: {
        src: [ '<%= env.frontEndSourcePath %>/js/unittests/specs/**/*' ],
        options: {
          mask: '**/*-spec.js',
          coverageFolder: '<%= env.frontEndSourcePath %>/js/unittests/coverage',
          excludes: [ '<%= env.frontEndSourcePath %>/js/unittests/specs/**/*' ],
          coverage: false
        }
      }
    },

    shell: {
      'build-require': {
        command: './require.sh'
      },

      'nose-chrome': {
        command: 'nosetests <%= env.testPath %> --tc=webdriver.browser:chrome --tc=testUrl:<%= env.testUrl %>',
        options: {
          stdout: true,
          stderr: true
        }
      },

      'nose-ie10': {
        command: 'nosetests <%= env.testPath %> --tc=webdriver.browser:ie10 --tc=testUrl:<%= env.testUrl %>',
        options: {
          stdout: true,
          stderr: true
        }
      }
    },

    /**
     * Watch: https://github.com/gruntjs/grunt-contrib-watch
     *
     * Run predefined tasks whenever watched file patterns are added, changed or deleted.
     * Add files to monitor below.
     */
    watch: {
      js: {
        files: [ 'Gruntfile.js', '<%= env.frontEndSourcePath %>/js/source/**/*.js' ],
        tasks: [ 'browserify:dev' ]
      },
      css: {
        files: [ '<%= env.frontEndSourcePath %>/css/less/**/*.less' ],
        tasks: [ 'less:dev' ]
      },
      options: {
        livereload: true
      }
    }
  } );

  grunt.event.on( 'coverage', function( lcov, done ) {
    require( 'coveralls' ).handleInput( lcov, function( err ) {
      if ( err ) {
        return done( err );
      }
      done();
    } );
  } );

  /**
   * The above tasks are loaded here.
   */
  require( 'load-grunt-tasks' )( grunt );

    /**
    * Create task aliases by registering new tasks
    * Let's remove `squish` since it's a duplicate task
    */
  grunt.registerTask( 'nose', [ 'shell:nose-chrome', 'shell:nose-ie10' ] );
  grunt.registerTask( 'test', [ 'eslint', 'mocha_istanbul', 'nose' ] );
  grunt.registerTask( 'test-js', [ 'eslint', 'mocha_istanbul' ] );
  grunt.registerTask( 'build', [ 'copy', 'squish' ] );
  grunt.registerTask( 'squish', [ 'browserify', 'uglify', 'less', 'cssmin' ] );
  grunt.registerTask( 'default', [ 'build', 'test-js' ] );
};
