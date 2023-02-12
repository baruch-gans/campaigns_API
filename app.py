from flask import Flask, jsonify, request

from logic import getCampaigns, getCampaign, saveCampaign

app = Flask(__name__)


@app.route('/campaigns', methods=['GET'])
def handleGetCampaigns():
    sortBy = request.args.get('sortBy')
    sortDirection = request.args.get('sortDirection', 'asc')
    campaigns = getCampaigns(sortBy, sortDirection)
    return jsonify(campaigns)


@app.route('/campaigns/<int:id>', methods=['GET'])
def handleGetCampaign(id):
    campaign = getCampaign(id)
    if campaign is not None:
        return jsonify(campaign)
    else:
        return jsonify({'error': f'Campaign with ID {id} not bfound'}), 404


@app.route('/campaigns', methods=['POST'])
def handleSaveCampaign():
    data = request.json
    campaign = saveCampaign(data)
    return jsonify(campaign)


if __name__ == "__main__":
    app.run(debug=True)


# TODO:
# Use pagination for large datasets,
# Use caching to reduce API calls
# Optimize API requests maybe

#  Add typing, enums, tests, divide into small functions
# Create separate file and class for validations
