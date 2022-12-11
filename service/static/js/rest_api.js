$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#recommendation_id").val(res.id);
        $("#recommendation_name").val(res.name);
        $("#recommendation_recommendation_id").val(res.recommendation_id);
        $("#recommendation_recommendation_name").val(res.recommendation_name);
        $("#recommendation_type").val(res.type);
        $("#recommendation_number_of_likes").val(res.number_of_likes);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#recommendation_name").val("");
        $("#recommendation_id").val("");
        $("#recommendation_recommendation_id").val("");
        $("#recommendation_recommendation_name").val("");
        $("#recommendation_type").val("");
        $("#recommendation_number_of_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#recommendation_name").val();
        let rec_product_id = $("#recommendation_recommendation_id").val();
        let rec_product_name = $("#recommendation_recommendation_name").val()
        let type = $("#recommendation_type").val();
        let number_of_likes = $("#recommendation_number_of_likes").val();

        let data = {
            "name": name,
            "recommendation_id": rec_product_id,
            "recommendation_name": rec_product_name,
            "type": type,
            "number_of_likes": number_of_likes
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();
        let name = $("#recommendation_name").val();
        let rec_product_id = $("#recommendation_recommendation_id").val();
        let rec_product_name = $("#recommendation_recommendation_name").val()
        let type = $("#recommendation_type").val();
        let number_of_likes = $("#recommendation_number_of_likes").val();

        let data = {
            "name": name,
            "recommendation_id": rec_product_id,
            "recommendation_name": rec_product_name,
            "type": type,
            "number_of_likes": number_of_likes
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${recommendation_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Like a Recommendation
    // ****************************************

    $("#like-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/recommendations/${recommendation_id}/like`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){

            update_form_data(res)
            flash_message("Recommendation has been Liked!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

     // ****************************************
    // Dislike a Recommendation
    // ****************************************

    $("#dislike-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/recommendations/${recommendation_id}/dislike`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Recommendation has been Disliked!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#recommendation_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#recommendation_name").val();
        let type = $("#recommendation_type").val();
        
        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (type) {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            console.log(res);
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Recommended Product ID</th>'
            table += '<th class="col-md-2">Recommended Product</th>'
            table += '<th class="col-md-2">Type</th>'
            table += '<th class="col-md-2">Number of Likes</th>'
            table += '</tr></thead><tbody>'
            let firstRec = "";
            for(let i = 0; i < res.length; i++) {
                let recommendation = res[i];
                table +=  `<tr id="row_${i}"><td>${recommendation.id}</td><td>${recommendation.name}</td><td>${recommendation.recommendation_id}</td><td>${recommendation.recommendation_name}</td><td>${recommendation.type}</td><td>${recommendation.number_of_likes}</td></tr>`;
                if (i == 0) {
                    firstRec = recommendation;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRec != "") {
                update_form_data(firstRec)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
