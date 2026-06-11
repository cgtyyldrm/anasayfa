FROM ruby:3.3.0-slim

ENV RAILS_SERVE_STATIC_FILES="true"
# Install dependencies
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    git \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /rails

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

# Precompile assets for production
RUN SECRET_KEY_BASE_DUMMY=1 bundle exec rails assets:precompile
# Entrypoint to run setups
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

EXPOSE 3000

CMD ["rails", "server", "-b", "0.0.0.0"]
