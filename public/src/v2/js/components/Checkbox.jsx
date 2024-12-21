import * as PropTypes from 'prop-types';
import React from 'react';

import cn from 'classnames';
import _isNil from 'lodash-es/isNil';

function computeTabIndex(disabled, tabIndex) {
  if (disabled) {
    return -1;
  }
  if (!_isNil(tabIndex)) {
    return tabIndex;
  }
}

const Checkbox = React.forwardRef(
  (
    {
      className = null,
      disabled = false,
      required = false,
      tabIndex = null,
      label,
      ...rest
    },
    ref
  ) => {
    const computedTabIndex = computeTabIndex(disabled, tabIndex);

    return (
      <label
        className={cn({
          'ui option checkbox': true,
          [className]: className !== null,
          disabled
        })}
      >
        <input
          type="checkbox"
          required={required}
          className="control__input"
          tabIndex={computedTabIndex}
          ref={ref}
          {...rest}
        />
        <span className="control__indicator" />
        <span className="control__description">{label}</span>
      </label>
    );
  }
);

Checkbox.propTypes = {
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.object]).isRequired,
  required: PropTypes.bool,
  checked: PropTypes.bool,
  onChange: PropTypes.func,
  tabIndex: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  value: PropTypes.string,
  /** Additional classes. */
  className: PropTypes.string,
  disabled: PropTypes.bool
};

export default Checkbox;
