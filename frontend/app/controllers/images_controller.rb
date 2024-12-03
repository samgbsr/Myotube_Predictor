# app/controllers/images_controller.rb
require 'net/http'
require 'uri'
require 'net/http/post/multipart'

class ImagesController < ApplicationController
  def index
    @images = Image.includes(:project).all
  end

  require 'net/http'
  require 'json'
  
  def create
    uploaded_file = params[:image][:file_name]
    project_id = params[:image][:project_id]
  
    uri = URI.parse('http://localhost:5000/process-image')
    request = Net::HTTP::Post::Multipart.new(
      uri.path,
      "image" => UploadIO.new(uploaded_file.tempfile, uploaded_file.content_type, uploaded_file.original_filename),
      "project_id" => project_id
    )
  
    response = Net::HTTP.start(uri.host, uri.port) do |http|
      http.request(request)
    end
  
    if response.is_a?(Net::HTTPSuccess)
      predictions = JSON.parse(response['predictions']) rescue []
      processed_image_data = response.body
  
      # Save the processed image and predictions
      image = Image.create!(
        file_name: uploaded_file.original_filename,
        project_id: project_id,
        myotube_amount: predictions.size,
        image_data: processed_image_data
      )
  
      # Save myotube data for the image
      predictions.each do |prediction|
        Myotube.create!(
          image_id: image.id,
          x_center: prediction['coords'][0],
          y_center: prediction['coords'][1],
          width: prediction['coords'][2],
          height: prediction['coords'][3],
          rotation: prediction['coords'][4],
          confidence: prediction['confidence'],
          type_class: prediction['class']
        )
      end
  
      # Update the project's myotube and picture counts
      project = Project.find(project_id)
      project.update!(
        myotube_count: project.images.joins(:myotubes).count,
        picture_count: project.images.count
      )
  
      flash[:success] = 'Image uploaded and processed successfully!'
    else
      flash[:error] = "Failed to process the image: #{response.message}"
    end
  
    redirect_to images_path
  end  

  def download
    image = Image.find(params[:id])
  
    send_data image.image_data,
              filename: image.file_name,
              type: 'image/png',
              disposition: 'attachment'
  end  
end
