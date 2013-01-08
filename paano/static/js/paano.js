(function($, undefined) {
    $(function() {
        $('.edit').on('click', function(e) {
            e.preventDefault();
            $("#content").load($(this).attr('href'), function() {
                var $questionContent = $('#question-content');
                $questionContent.filedrop({
                    url: '/upload',
                    withCredentials: true,
                    allowedfiletypes: ['image/jpeg','image/png','image/gif'],
                    uploadFinished: function(i, file, response, time) {
                        var imageMD = '![alt text](' + response.filename + ')';
                        $questionContent.val($questionContent.val() + imageMD);
                    }
                });
            });
        });

    });
})(jQuery);