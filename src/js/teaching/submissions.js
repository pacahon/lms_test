let filterAssignmentForm = $(".filters form");

let assignmentSelect = $("#assignments-select");

const fn = {
    launch: function () {
        fn.initFiltersForm();
    },

    initFiltersForm: function() {
        assignmentSelect.selectpicker({
            maxOptions: 2,
            iconBase: 'fa',
            tickIcon: 'fa-check'
        });
        assignmentSelect.on('loaded.bs.select', function (e) {
          $(this).closest('.filters').find('.loading').remove();
        });

        // TODO: simplify
        filterAssignmentForm.on('submit', function () {
            let selected = $.map(assignmentSelect.find('option:selected'), function (el, i) {
                return $(el).val();
            });
            let selectedAssignments = selected.join(",");
            window.location = filterAssignmentForm.attr("action") + selectedAssignments;
            return false;
        })
    },
};

export default fn;