class Parser
  def parse(score_text)
    begin
      score_text.scan(SCORE_PATTERN) do |match|
        handle_match(match)
      end
    rescue err : ParseError
      # handle error ...
    end
  end
end

