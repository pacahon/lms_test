import _isNil from 'lodash-es/isNil';
import React from 'react';
import classNames from 'classnames';
import * as PropTypes from 'prop-types';

function computeTabIndex(disabled, tabIndex) {
  if (disabled) {
    return -1;
  }
  if (!_isNil(tabIndex)) {
    return tabIndex;
  }
}

const Checkbox = React.forwardRef(function Checkbox(props, ref) {
  const {
    className = '',
    disabled = false,
    required = false,
    tabIndex = null,
    label,
    ...rest
  } = props;
  const computedTabIndex = computeTabIndex(disabled, tabIndex);

  let wrapperClass = classNames({
    checkbox: true,
    [className]: className.length > 0,
    disabled: disabled
  });

  return (
    <div className={wrapperClass}>
      <label>
        <input
          type="checkbox"
          required={required}
          tabIndex={computedTabIndex}
          ref={ref}
          {...rest}
        />
        {` ${label}`}
      </label>
    </div>
  );
});

Checkbox.propTypes = {
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.object]).isRequired,
  required: PropTypes.bool,
  checked: PropTypes.bool,
  onChange: PropTypes.func,
  tabIndex: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  /** Additional classes. */
  className: PropTypes.string,
  disabled: PropTypes.bool
};

export default Checkbox;
