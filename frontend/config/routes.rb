Rails.application.routes.draw do
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Render dynamic PWA files from app/views/pwa/*
  get "service-worker" => "rails/pwa#service_worker", as: :pwa_service_worker
  get "manifest" => "rails/pwa#manifest", as: :pwa_manifest

  # Defines the root path route ("/")
  # root "posts#index"
  
  # api routes
  namespace :api do
    resources :images, only: [:create]
  end
  get '/images/:id/download', to: 'images#download', as: 'download_image'

  # config/routes.rb
  resources :projects, only: [:index]
  resources :images, only: [:index, :create]
  resources :myotubes, only: [:index]
  resources :images do
    member do
      get :show_image
    end
  end
  
  
end
