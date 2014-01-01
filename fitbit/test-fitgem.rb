#!/usr/bin/env ruby

require "fitgem"
require "pp"
require "yaml"
require "pry"

# Load the existing yml config
config = begin
  Fitgem::Client.symbolize_keys(YAML.load(File.open(".fitgem.yml")))
rescue ArgumentError => e
  puts "Could not parse YAML: #{e.message}"
  exit
end

client = Fitgem::Client.new(config[:oauth])

# With the token and secret, we will try to use them
# to reconstitute a usable Fitgem::Client
if config[:oauth][:token] && config[:oauth][:secret]
  begin
    access_token = client.reconnect(config[:oauth][:token], config[:oauth][:secret])
  rescue Exception => e
    puts "Error: Could not reconnect Fitgem::Client due to invalid keys in .fitgem.yml"
    exit
  end
# Without the secret and token, initialize the Fitgem::Client
# and send the user to login and get a verifier token
else
  request_token = client.request_token
  token = request_token.token
  secret = request_token.secret

  puts "Go to http://www.fitbit.com/oauth/authorize?oauth_token=#{token} and then enter the verifier code below"
  verifier = gets.chomp

  begin
    access_token = client.authorize(token, secret, { :oauth_verifier => verifier })
  rescue Exception => e
    puts "Error: Could not authorize Fitgem::Client with supplied oauth verifier"
    exit
  end

  puts 'Verifier is: '+verifier
  puts "Token is:    "+access_token.token
  puts "Secret is:   "+access_token.secret

  user_id = client.user_info['user']['encodedId']
  puts "Current User is: "+user_id

  config[:oauth].merge!(:token => access_token.token, :secret => access_token.secret, :user_id => user_id)

  # Write the whole oauth token set back to the config file
  File.open(".fitgem.yml", "w") {|f| f.write(config.to_yaml) }
end

# ============================================================
# Add Fitgem API calls on the client object below this line

#pp client.activities_on_date 'today'

def avg_time(data)
  #pp data
  total = 0
  count = 0
  data.each do |_, list|
    list.each do |v|
      unless v["value"].empty?
        hour,min = v["value"].split(':')
        if hour.to_i >= 21
          total += hour.to_i * 60 + min.to_i
          count += 1
        elsif hour.to_i <= 6
          total += 24*60 + hour.to_i * 60 + min.to_i
          count += 1
        end
      end
    end
  end
  avg_hour = total / count / 60 % 24
  avg_min = total / count % 60
  puts "#{avg_hour}:#{avg_min}"
end

def avg(data, thres=0)
  #pp data
  values = []
  cnt = 0
  data.each do |_, list|
    list.each do |v|
      if v["value"].to_i > thres
        cnt += 1
      end
      values << v["value"].to_i if v["value"] != "0"
    end
  end
  avg = values.inject(0.0) { |sum, el| sum + el } / values.size
  puts "avg: #{avg}, cnt: #{cnt}"
end

date_range = {:base_date => '2013-01-01', :end_date => '2013-12-30'}

puts "sleep/startTime"
avg_time client.data_by_time_range('/sleep/startTime', date_range)

puts "sleep/timeInBed"
avg client.data_by_time_range('/sleep/timeInBed', date_range)

puts "sleep/minutesAsleep"
avg client.data_by_time_range('/sleep/minutesAsleep', date_range)

puts "sleep/minutesToFallAsleep"
avg client.data_by_time_range('/sleep/minutesToFallAsleep', date_range)

puts "log/steps"
avg client.data_by_time_range('/activities/log/steps', date_range), 10000

puts "log/floors"
avg client.data_by_time_range('/activities/log/floors', date_range)
