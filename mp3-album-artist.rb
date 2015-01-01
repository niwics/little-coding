#!/usr/bin/ruby

# author: niwi.cz, January 2012
# Program rekurzivně projde složku a pokud najde soubor cover.jpg, tak jej zmenší na požadované maximální rozměry a přiřadí ke všem mp3 souborům v daném podadresáři.
# Spuštění: album-artist path/to/folder [max_image_size_in_kB]

require "fileutils"
require 'rubygems'
require 'RMagick'
require 'id3lib'

include Magick

class AlbumArtist
  
  DEBUG = true
  DEFAULT_IMG_LIMIT = 800 # kB
  HELP_NAMES = ['help', '-help', '-h', '--help', '--h']

  def initialize
    @path = nil
    @img_limit = 0
    
    @clear = false
    @debug = false
    @show_frees = false
    @replace = false
  
    parse_params
    scan_folders @path
  end
  
  
  def scan_folders path
    if !File.exist?(path)
      return err "Could not locate the root folder \"" + path + "\"."
    end
    deb "Entering the directory " + path + "..."
    
    tag = nil
    cover_full = path + "/cover.jpg"
    cover_exists = File.exists?(cover_full)
    covertag = nil
    cover_shrink = nil
    clear = new_cover = false
    
    
    # process all files
    Dir.entries(path).each do |filename|
      if filename == "." or filename == ".."
        next
      end
      # Recurse into the directory...
      if File.directory?(path+'/'+filename)
        scan_folders path+'/'+filename
        next
      end
      # handle image miniature
      if filename =~ /.*\.mp3$/
        if @clear
          clear = true
        end
        if cover_exists
          tag = ID3Lib::Tag.new(path+'/'+filename)
          if tag.frame(:APIC)
            if @replace
              deb "Replacing album art for the file " + path + "/" + filename
              new_cover = true
            else
              deb "Album art exists yet for the file " + path + "/" + filename
            end
          else
            new_cover = true
          end
        end
        
        
        
        if new_cover
          if !covertag
            cover_shrink = get_shrinked_cover path
            cover = cover_shrink ? cover_shrink : cover_full
            covertag = {
              :id          => :APIC,
              :mimetype    => 'image/jpeg',
              :picturetype => 3,
              :description => 'Album Art',
              :textenc     => 0,
              :data        => File.read(cover)
            }
          end
          tag << covertag

          # Last but not least, apply changes
          tag.update!
        end
      end
    end
    
    # remove miniature if created
    if cover_shrink
      File.delete(cover_shrink)
    end
  end
  
  def get_shrinked_cover path
    cover_src = path + "/cover.jpg"
    if File.exists?(cover_src)
      if @img_limit > 0 and File.stat(cover_src).size > @img_limit
        deb "Shrinking cover image..."
        cover_min = path + "/tmp_cover_album_artist.jpg"
        miniature = Image.read(cover_src).first
        miniature.change_geometry!('800x800') { |cols, rows, img|
          miniature.resize!(cols, rows)
        }
        miniature.write(cover_min)
        return cover_min
      end
    end
  end




  # parse params
  def parse_params
    param1 = ARGV.shift
    if !param1
      err 'Parameter with folder was not set.'
      print_help_and_exit
    elsif HELP_NAMES.include?param1
      print_help_and_exit
    end
    
    if param1[0,1] == '-'
      @params = param1
      @path = ARGV.shift
      if !@path
        err 'Parameter with folder was not set.'
        print_help_and_exit
      end
    else
      @path = param1
    end
    
    if @path[-1,1] == '/'
      @path = @path[0, @path.length-1]
    end
    
    @img_limit = ARGV.shift
    if !@img_limit
      @img_limit = DEFAULT_IMG_LIMIT
    else
      @img_limit = @img_limit.to_i
    end
    
    # check possible params
    if @params != nil
      @params = @params[1..-1] # is frozen...
      @params.each_char do |i|
        case i
        when 'c' then @clear = true
        when 'f' then @show_frees = true
        when 'g' then @debug = true
        when 'h' then print_help_and_exit
        when 'r' then @replace = true
        else
          err 'Unknown switch: "' + i + '". See help (-h) for more informations.'
          return false
        end
      end
    else
      @params = ''
    end
  end


  def print_help_and_exit
    puts <<EOT
----------------------------
 Album Artish program help
----------------------------
Program rekurzivně projde složku a pokud najde soubor cover.jpg, tak jej zmenší na požadované maximální rozměry a přiřadí ke všem mp3 souborům v daném podadresáři.

Spuštění: album-artist path/to/folder [max_image_size_in_kB]

Author: Miroslav Kvasnica, niwi.cz
Date: leden 2012
EOT
    exit
    echo "hoho"
  end


  def err (message)
    echo("!!! " + message, false)
    @error = true
    return false
  end


  def echo (message, formatted = true, newline = true)
    msg = (formatted ? '> ' :'') + message.to_s
    print msg + (newline ? "\n" : "")
  end
  
  def deb message
    if DEBUG
      echo ">> " + message
    end
  end
  
end

app = AlbumArtist.new()
