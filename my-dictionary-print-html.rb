#!/usr/bin/ruby

# author: niwi.cz, 2011

require "fileutils"

class Printer

  @test
  @std_output
  @infilename
  @output
  @current_table
  PAGE_COLS = 3
  POSSIBLE_PARAMS = ['t', 'o']
  HEADING = '<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Dictionary</title>
  <style type="text/css">
    body {font-size: 11px; font-family: Arial, Helvetica, sans-serif;}
    h1 {margin: 0; font-size: 14px; text-align: center}
    h2 {margin: 0; border-bottom: 1px solid gray; font-size: 13px}
    table {margin: 0; border: none; border-collapse: collapse;}
    td {padding: 2px 5px; text-align: right}
    td.trans {padding-left: 2px; text-align: left}
    td.heading {text-align: left}
  </style>
  '
  
  def initialize
    @output = ''
    @current_table = Array.new

    parse_params

    # can read infile?
    if !File.readable? @infilename
      $stderr.puts "Can not read the file: " + @infilename + "."
      display_help
      exit
    end
  end

  
  def parse
    out HEADING + "<body>\n<html>\n<table>\n"
    File.open(@infilename) do |infile|
      while (line = infile.gets)
        parse_line line
      end
    end
    out print_table + "</table>\n\n</body>\n</html>"
  end


  def parse_line (line)
    line.gsub!('\r\n', '')
    line.gsub!(/=+/, '')
    line.strip!
    if line == ''
      return nil
    end
    index = line.index(';')
    if !index
      if line.index('@') == 0
        out '<h1>' + line[1..-1] + '</h1>'
      else
        print_heading line
      end
    else
      print_item(line[0..index-1], line[index+1..-1])
    end
  end


  def print_heading (text)
    if @current_table
      out print_table
      @current_table = Array.new
    end
    out '<tr><td colspan="'+ ((2*PAGE_COLS).to_s) +'" class="heading"><h2>' + text + '</h2></td></tr>'
  end


  def print_item(src, dst)
    if src == '' or dst == ''
      $stderr.puts 'Incomplete: ' + src + ';' + dst
    end
    # add spaces after colons
    src.gsub!(/\s+,\s+/, ',')
    src.gsub!(/,/, ', ')
    dst.gsub!(/\s+,\s+/, ',')
    dst.gsub!(/,/, ', ')
    @current_table << Array[src, dst]
  end

  def out string
    if !@test
      @output += string
    end
  end

  def print_table
    str = ''
    curr = 0
    @current_table.each do |item|
      if curr == 0
        str += "\n<tr>\n"
      end
      str += '<td>' + item[0] + '</td><td class="trans">- ' + item[1] + '</td>'
      curr = (curr+1) % PAGE_COLS
      if curr == 0
        str += "\n</tr>\n"
      end
    end
    # add empty cells to the end
    if curr != 0
      while curr != 0
        str += '<td class="empty"></td><td class="empty trans"></td>'
        curr = (curr+1) % PAGE_COLS
      end
      str += "\n</tr>\n"
    end
    return str
  end



  # parse params
  def parse_params
    
    # get input file
    @infilename = ARGV.shift
    if !@infilename
      display_help
      exit
    end
    params = ARGV.shift

    # check possible params
    if params != nil
      params = params[1..-1] # is frozen...
      params.each_char do |i|
        case i
        when 't' then @test = true
        when 'o' then @std_output = true
        else
          $stderr.puts 'Invalid option: "' + i + '".'
          $stderr.puts 'Allowed options: "' + POSSIBLE_PARAMS.join('", "') + '".'
          return false
        end
      end
    else
      params = ''
    end
  end

  def output
    if @std_output
      puts @output
    else
      file = File.open('output.html', 'w')
      file.puts(@output)
    end
  end


  def display_help
    puts "print-html.rb input-file-path [params].
   Parameters:
    -t Tests the input file - searches for malformation and non- translated words
    -o Outputs result to the stdout
    "
  end
end

p = Printer.new
p.parse
p.output
