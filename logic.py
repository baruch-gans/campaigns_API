import json
from datetime import datetime

import requests

CAMPAIGNS_FILE = 'db.json'
DELIVERY_ENDPOINT = 'http://api.ironsrc.com/interview/delivery/{}'
STATS_ENDPOINT = 'http://api.ironsrc.com/interview/stats'


def getCampaigns(sortBy, sortDirection):
    with open(CAMPAIGNS_FILE) as f:
        campaigns = json.load(f)
    for campaign in campaigns:
        updateCampaignFromDelivery(campaign)
    updateCampaignsFromStats(campaigns)
    if sortBy is not None:
        campaigns = sorted(campaigns, key=lambda x: x[sortBy], reverse=sortDirection == 'desc')
    return campaigns


def getCampaign(id):
    with open(CAMPAIGNS_FILE) as f:
        campaigns = json.load(f)
    campaign = next((c for c in campaigns if c['id'] == id), None)
    if campaign is not None:
        updateCampaignFromDelivery(campaign)
        updateCampaignsFromStats([campaign])
    return campaign


def saveCampaign(data):
    name = data.get('name')
    startDate = data.get('startDate')
    bid = data.get('bid')

    if name is None or len(name) > 200:
        return {'error': 'Invalid name'}

    if startDate is not None:
        try:
            datetime.strptime(startDate, '%Y-%m-%d')
        except ValueError:
            return {'error': 'Invalid start date'}

    if bid is None or not 0.001 <= bid <= 150:
        return {'error': 'Invalid bid'}

    with open(CAMPAIGNS_FILE) as f:
        campaigns = json.load(f)
    id = max(c['id'] for c in campaigns) + 1 if len(campaigns) > 0 else 1
    campaign = {
        'id': id,
        'name': name,
        'startDate': startDate,
        'bid': bid,
        'status': 'Pending',
        'views': 0,
        'clicks': 0,
        'installs': 0,
    }
    campaigns.append(campaign)
    with open(CAMPAIGNS_FILE, 'w') as f:
        json.dump(campaigns, f, indent=2)
    updateCampaignFromDelivery(campaign)
    updateCampaignsFromStats([campaign])
    return campaign


def updateCampaignFromDelivery(campaign):
    url = DELIVERY_ENDPOINT.format(campaign['id'])
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        campaign['status'] = data['status']
    else:
        print(f'Error updating campaign {campaign["id"]} from delivery endpoint: {response.status_code}')


def updateCampaignsFromStats(campaigns):
    ids = [c['id'] for c in campaigns]
    url = f'{STATS_ENDPOINT}?ids={",".join(str(id) for id in ids)}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            campaign = next((c for c in campaigns if c['id'] == item['campaign_id']), None)
            if campaign is not None:
                campaign['views'] = item['impressions']
                campaign['clicks'] = item['clicks']
                campaign['installs'] = item['installs']
    else:
        print(f'Error updating campaigns from stats endpoint: {response.status_code}')
