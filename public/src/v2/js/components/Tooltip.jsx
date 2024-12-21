import * as PropTypes from 'prop-types';
import React from 'react';

import { Tooltip as BaseTooltip } from 'react-tippy';

export const Tooltip = ({ title, children, ...options }) => (
  <BaseTooltip
    animation={`fade`}
    arrow={true}
    arrowSize={`small`}
    size={`regular`}
    theme={`dark`}
    {...options}
    title={title}
  >
    {children}
  </BaseTooltip>
);

Tooltip.propTypes = {
  title: PropTypes.string,
  children: PropTypes.element.isRequired
};

export const Hint = ({ ...options }) => (
  <Tooltip {...options}>
    <span className="tooltip__icon _rounded">?</span>
  </Tooltip>
);
