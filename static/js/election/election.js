$('input:radio').change(function () {
    var value = $(this).val();

    var post = $(this).data('post');
    var candidate = $(this).data('candidate');

    change_candidates_color(post, candidate, value);

});


function change_candidates_color(post, candidate, value) {
    var current_selection = post_selection[post].slice();
    var max_vote = post_count[post];

    for (var i = 0; i < current_selection.length; i++) {
        if (current_selection[i][0] == candidate) {
            current_selection.splice(i, 1);
            break;
        }
    }

    if (current_selection.length == max_vote) {
        current_selection.shift();
    }
    current_selection.push([candidate, value]);

    reset_post_candidates(post);

    current_selection.forEach(function (candidate) {
        var candidate_poster_div = $('#candidate-{0}-poster'.format(candidate[0]));
        if (candidate[1] == 1) {
            candidate_poster_div.addClass('accepted-candidate');
            $('#candidate-{0}-yes'.format(candidate[0])).prop('checked', true);
        }
        else if (candidate[1] == -1) {
            candidate_poster_div.addClass('rejected-candidate');
            $('#candidate-{0}-no'.format(candidate[0])).prop('checked', true);
        }
    });

    post_selection[post] = current_selection;
}

function reset_post_candidates(post) {
    var post_candidates = $('#post-{0} .candidate-poster'.format(post));

    post_candidates.each(function () {
        $(this).removeClass('accepted-candidate');
        $(this).removeClass('rejected-candidate');
        $('#candidate-{0}-neutral'.format($(this).data('candidate'))).prop('checked', true);
    });

}

$('#submit-vote').submit(function (event) {

    var election = $(this).data('election');
    var election_votes = $('#election-{0} input:checked'.format(election));

    var voter_vote = {};

    election_votes.each(function() {
        voter_vote[$(this).data('candidate')] = parseInt($(this).val());
    });

    $("#submit-form-votes-inp").val(JSON.stringify(voter_vote));

});
