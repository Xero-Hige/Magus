# Committing changes to a repo via the Github API is not entirely trivial.
# The five-step process is outlined here:
#   http://developer.github.com/v3/git/
#
# Matt Swanson wrote a blog post translating the above steps into actual API calls:
#   http://swanson.github.com/blog/2011/07/23/digging-around-the-github-api-take-2.html
#
# I was not able to find sample code for actually doing this in Ruby,
# either via the HTTP API or any of the gems that wrap the API.
# So in the hopes it will help others, here is a simple function to
# commit a single file to github via the API.  The code only handles
# the case of committing a single file to the master branch,
# but should be easy to modify for your own needs.
#
# Note also that we use HTTP basic auth, not OAuth, in this example.
#
# Prerequisites:
#
#   $ gem install rest-client
#   $ export GITHUB_USER=xxxx
#   $ export GITHUB_PASS=yyyy
#
# Usage:
#
#   push_to_github :path => "path/to/file.txt", :content => "hello commit", :repo => 'test'
#
# In the above example, the repo 'test' must be owned by GH_USERNAME, and have at least one commit.
#
# No news is good news.  If you don't raise exceptions, you should see the commit in your repo.
#
# CC0 Public Domain Dedication
# To the extent possible under law, Harlan T Wood
# has waived all copyright and related or neighboring
# rights to this work.
# http://creativecommons.org/publicdomain/zero/1.0/
#

require 'rest_client'
require 'json'

def push_to_github(params)
  repo = params[:repo]

  # get the head of the master branch
  # see http://developer.github.com/v3/git/refs/
  branch = github(:get, repo, "refs/heads/tweets")
  last_commit_sha = branch['object']['sha']

  # get the last commit
  # see http://developer.github.com/v3/git/commits/
  last_commit = github :get, repo, "commits/#{last_commit_sha}"
  last_tree_sha = last_commit['tree']['sha']

  # create tree object (also implicitly creates a blob based on content)
  # see http://developer.github.com/v3/git/trees/
  new_content_tree = github :post, repo, :trees,
                            :base_tree => last_tree_sha,
                            :tree => [{:path => params[:path], :content => params[:content], :mode => '100644'}]
  new_content_tree_sha = new_content_tree['sha']

  # create commit
  # see http://developer.github.com/v3/git/commits/
  new_commit = github :post, repo, :commits,
                      :parents => [last_commit_sha],
                      :tree => new_content_tree_sha,
                      :message => 'commit via api'
  new_commit_sha = new_commit['sha']

  # update branch to point to new commit
  # see http://developer.github.com/v3/git/refs/
  github :patch, repo, "refs/heads/tweets",
         :sha => new_commit_sha
end

def github(method, repo, resource, params={})
  resource_url = "https://#{ENV['GITHUB_USER']}:#{ENV['GITHUB_PASS']}@api.github.com" +
    "/repos/#{ENV['GITHUB_USER']}/#{repo}/git/#{resource}"
  if params.empty?
    JSON.parse RestClient.send(method, resource_url)
  else
    JSON.parse RestClient.send(method, resource_url, params.to_json, :content_type => :json, :accept => :json)
  end
end

puts #{ENV['GITHUB_USER']}
push_to_github :path => ARGV[0], :content => File.read(ARGV[1]), :repo => 'Magus'