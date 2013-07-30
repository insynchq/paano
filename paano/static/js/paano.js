(function($, undefined) {
    $(function() {

        $('#paano-platform').on('change', function(e) {
            location.href = $(this).val();
        });

        $('.paano-edit').on('click', function(e) {
            e.preventDefault();
            $("#paano-content").load($(this).attr('href'), function() {
                var $questionContent = $('#paano-question-content');
                $questionContent.filedrop({
                    url: '../../../../upload',
                    withCredentials: true,
                    allowedfiletypes: ['image/jpeg','image/png','image/gif'],
                    uploadFinished: function(i, file, response, time) {
                        var imageMD = '![alt text](' + response.filename + ')';
                        $questionContent.val($questionContent.val() + imageMD);
                    }
                });
            });
        });

        $('.paano-delete').on('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this item?')) {
                var promise = $.ajax({
                    url: $(this).attr('href'),
                    type: 'delete'
                });
                promise.done(function(response) {
                    location.href = '/';
                });
                promise.fail(function() {
                    alert('Failed to delete item. Please try again.');
                });
            }
        });

    });
})(jQuery);
