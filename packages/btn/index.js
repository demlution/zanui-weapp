const nativeButtonBehavior = require('./native-button-behaviors');

Component({
  externalClasses: ['custom-class', 'theme-class'],
  behaviors: [nativeButtonBehavior],
  relations: {
    '../plugin-comzbtngroup/index': {
      type: 'parent',
      linked() {
        this.setData({ inGroup: true });
      },
      unlinked() {
        this.setData({ inGroup: false });
      }
    }
  },
  properties: {
    type: {
      type: String,
      value: '',
    },
    size: {
      type: String,
      value: '',
    },
    plain: {
      type: Boolean,
      value: false,
    },
    disabled: {
      type: Boolean,
      value: false,
    },
    loading: {
      type: Boolean,
      value: false,
    }
  },

  data: {
    inGroup: false,
    isLast: false
  },

  methods: {
    handleTap() {
      if (this.data.disabled) {
        this.triggerEvent('disabledclick')
        return;
      }
      this.triggerEvent('btnclick');
    },

    switchLastButtonStatus(isLast = false) {
      this.setData({ isLast });
    }
  }
});
