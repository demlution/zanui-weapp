Component({
  externalClasses: ['col-class'],

  relations: {
    '../plugin-comzrow/index': {
      type: 'parent'
    }
  },

  properties: {
    col: {
      value: 0,
      type: Number
    },
    offset: {
      value: 0,
      type: Number
    }
  }
});
