require 'sinatra' # For responding to POST requests from Node Server
require 'open-uri'
require 'nokogiri'
require 'json'

class String
  # convert a string fraction to float fraction
  def to_frac
    numerator, denominator = split('/').map(&:to_f)
    denominator ||= 1
    numerator/denominator
  end
end

def extractName(doc)
  # Looks for 'name' tag in html and extract the content
  res = ""
  doc.css("h1[itemprop=name]").each do |row|
    res = res + row.content
  end
  return res
end

def extractAlgorithm(doc)
  # From the division - directions, extract each step of the recipe and return the list as a string.
  res ||= []
  doc.css("div.directions li span").each do |row|
    res << row.content
  end
  res = res.join("@")
  return res
end

def extractTime(steps)
  # Looks for certain keywords in steps of recipes, converts it into minutes and store it in string.
  @time_keywords = {"hour" => 60.0, "minute" => 1.0, "second" => 0.01666667}
  res = []
  steps = steps.split("@")
  steps.each do |step|
    units = []
    @time_keywords.each do |unit, val|
      units << unit if step.include? unit
    end
    res << findTimeVal(step, units)
  end
  res = res.join("@")
  return res
end

def findTimeVal(string, units)
  # Given a string and units array, return the list of all timing information in the string.
  return "0" if units.empty?
  res = ""
  list_str = createTimeMap(string, units)
  list_str.each do |key, val|
     temp = []
    val.each do |str|
      temp << /\d(.*\d+)?/.match(str)[0].split()[-1]
    end
    list_str[key] = temp
  end
  
  list_str.each do |key, val|
    val.each do |amt|
      if res.empty?
        res += ((@time_keywords[key] * amt.to_frac * 100).round / 100.0).to_s
      else
        res += ";" + ((@time_keywords[key] * amt.to_frac * 100).round / 100.0).to_s
      end
    end
  end
  return res
end

def createTimeMap(string, units)
  # Create a map of timings available in string
  list_str = {}
  string = string.split()
  temp = ""
  string.each do |word|
    flag = ""
    units.each do |unit|
      flag = unit if word.include? unit
    end
    if flag.empty?
      temp += word + " "
    else
      if temp =~ /\d/
        if list_str.has_key? flag
          list_str[flag] << temp
        else
          list_str[flag] = [temp]
        end
      end
      temp = ""
    end
  end
  return list_str
end

def extractIngredient(site)
  # Extract ingredients from site and return a string containing other elements, solids/liquids and all ingredient list
  @conversion_dic_solids = {"tablespoon" => 14.3, "ounce" => 28.35, "pound" => 453.6, "cup" => 226.8, "teaspoon" => 4, "gram" => 1 }
  @conversion_dic_liquids = {"tablespoon" => 15, "cup" => 237, "teaspoon" => 5, "fluid ounce" => 30, "pint" => 473, "gallon" => 3785, "liter" => 1000, "quart" => 946.25 }
  
  @exclude_liquids = ['milk', 'oil', 'juice', 'water', 'puree']
  raw_map = createIngredientMap(site)
  solids = {}
  liquids = {}
  others = []
  flag = 0
  raw_map.each do |key, val|
    if val
      @conversion_dic_solids.each do |unit, amt|
        if val.include? unit and not(@exclude_liquids.any? {|word| key.include? word})
          raw_map[key] = (extractQty(raw_map[key], unit) * amt).round
          flag = 1
          break
        end
      end
      @conversion_dic_liquids.each do |unit, amt|
        if val.include? unit and @exclude_liquids.any? {|word| key.include? word}
          raw_map[key] = (extractQty(raw_map[key], unit) * amt).round
          flag = 2
          break
        end
      end
    end
    solids[key] = raw_map[key].to_s if flag == 1
    liquids[key] = raw_map[key].to_s if flag == 2
    others << raw_map[key].to_s + " " + key if flag == 0
    flag = 0
  end
  
  others = others.reject {|i| i.ord == 32}
  others = others.join("@")
  ingrList = solids.keys()
  solids = solids.map {|k,vs| "#{k}@#{vs}"}.join("@0@")
  solids = solids + "@0"
  res = solids
  if not liquids.empty?
    ingrList += liquids.keys()
    liquids = liquids.map {|k,vs| "#{k}@#{vs}"}.join("@1@")
    liquids = liquids + "@1"
    res = res + "@" + liquids
  end
  return res, others, ingrList
end

def extractQty(string, unit)
  # Extract quantity corresponding to the unit in string
  x = /(.*?)#{unit}/.match(string)[0]
  x.gsub!(unit, "")
  x = x.split().map {|t| /\d+(\/\d+)?/.match(t)[0]}
  x = x.map {|t| t.to_frac}
  return x.inject(:+) if x[-1] < 1.0
  return x[-1]
end

def createIngredientMap(doc)
  # Create a map of ingredient with quantities
  res = {}
  doc.css("p[itemprop=ingredients]").each do |row|
    temp = row.content.split("\r\n").map {|x| x.strip}
    temp.reject! {|x| x.empty?}
    res[temp[1]] = temp[0] if temp.size == 2
    res[temp[0]] = nil unless temp.size == 2
  end
  return res
end

def extractImage(doc)
  # Extract image from site
  img_srcs = doc.css("div#divHeroPhotoContainer img").map{ |i| i['src'] }[0]
  return img_srcs
end

def extractRating(doc)
  # Extract rating from site
  rating = doc.css("div[itemprop='aggregateRating'] div.rating-stars-img meta").map{|i| i['content']}[0]
  rating = ((rating.to_frac * 100).round / 100.0).to_s
  return rating
end

def findCommonWords(str1, str2)
  #Given two strings, return an array of common words.
  res = []
  str1.split().each do |word|
    word = word.gsub(/,/,'')
    if str2.index(word)
      res << word
    end
  end
  return res[-1] unless res.empty?
  return "choo"
end

def orderIngredients(ingrList, steps)
  # Create a string of ingredients in the order they occur in the steps.
  ingrList2 = ingrList.map(&:downcase)
  steps.downcase!
  steps = steps.split('@')
  res= []
  steps.each do |step|
    temp = {}
    s = []
    ingrList2.each_with_index do |ingr, idx|
      if not findCommonWords(ingr, step) == "choo"
        temp[step.index(findCommonWords(ingr, step))] = ingrList[idx]
      end
    end
    temp.sort.each do |ingr|
      s << ingr[1]
    end
    s = s.join('@')
    res << s
  end
  res = res.join('^')
  return res
end

def createJson(site_url)
  # Create a Json object in the specified format
  site = Nokogiri::HTML(open(site_url))
  res = {}
  res["recipename"] = extractName(site)
  temp = extractIngredient(site)
  res["ingrs"] = temp[0]
  res["other"] = temp[1]
  lst = temp[2]
  temp = extractAlgorithm(site)
  res["orderedIngrs"] = orderIngredients(lst, temp)
  res["steps"] = temp
  res["time"] = extractTime(temp)
  res["image"] = extractImage(site)
  res["rating"] = extractRating(site)
  return JSON.generate(res)
end

# eg1 = "http://allrecipes.com/Recipe/Baked-Macaroni-and-Cheese/Detail.aspx?evt19=1&referringHubId=509"
# eg2 = "http://allrecipes.com/Recipe/Mozechilli-Casserole/?prop24=hn_slide1_Mozechilli-Casserole&evt19=1"
# eg3 = "http://allrecipes.com/recipe/tangy-honey-glazed-ham/?prop24=hn_slide1_Tangy-Honey-Glazed-Ham&evt19=1"
# eg4 = "http://allrecipes.com/Recipe/Apricot-Brown-Sugar-Ham/Detail.aspx?src=VD_Summary"
# eg5="http://allrecipes.com/Recipe/Joes-General-Tsos-Chicken/?prop31=5"
#
# p  createJson(eg1)
# p createJson(eg2)
# p createJson(eg3)
# p createJson(eg4)
# p createJson(eg5)

post '/recipe' do
  createJson(params[:recipe_url])
end

    


