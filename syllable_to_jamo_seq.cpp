#include <iostream>
#include <vector>
#include <wchar.h>
#include <locale>

// reference: https://social.msdn.microsoft.com/Forums/vstudio/ko-KR/991e9328-0fe7-43a1-9eb4-eee5ff04aac7/5462044544-52488-51473-5133349457-48516475325461644592?forum=visualcplusko
unsigned int BreakHan(const wchar_t* str, wchar_t* buffer, unsigned int nSize)
{
    //초성
    static const wchar_t wcHead[] = {
        L'ㄱ', L'ㄲ', L'ㄴ', L'ㄷ',
        L'ㄸ', L'ㄹ', L'ㅁ', L'ㅂ',
        L'ㅃ', L'ㅅ', L'ㅆ', L'ㅇ',
        L'ㅈ', L'ㅉ', L'ㅊ', L'ㅋ',
        L'ㅌ', L'ㅍ', L'ㅎ'};

    //중성
    static const wchar_t wcMid[] = {
        L'ㅏ', L'ㅐ', L'ㅑ', L'ㅒ',
        L'ㅓ', L'ㅔ', L'ㅕ', L'ㅖ',
        L'ㅗ', L'ㅘ', L'ㅙ', L'ㅚ',
        L'ㅛ', L'ㅜ', L'ㅝ', L'ㅞ',
        L'ㅟ', L'ㅠ', L'ㅡ', L'ㅢ', L'ㅣ'};

    //종성
    static const wchar_t wcTail[] = {
        L' ', L'ㄱ', L'ㄲ', L'ㄳ',
        L'ㄴ', L'ㄵ', L'ㄶ', L'ㄷ',
        L'ㄹ', L'ㄺ', L'ㄻ', L'ㄼ',
        L'ㄽ', L'ㄾ', L'ㄿ', L'ㅀ',
        L'ㅁ', L'ㅂ', L'ㅄ', L'ㅅ',
        L'ㅆ', L'ㅇ', L'ㅈ', L'ㅊ',
        L'ㅋ', L'ㅌ', L'ㅍ', L'ㅎ'};

    unsigned int pos = 0;

    while(*str != '\0') {
        if (0xAC00 <= *str && *str <= 0xD7A3) {  // between '가' and '힣'
            if (pos + 3 > nSize - 1)
                break;

            buffer[pos] = wcHead[(*str - 0xAC00) / (21*28)];
            buffer[pos+1] = wcMid[(*str - 0xAC00) % (21 * 28) / 28];
            buffer[pos+2] = wcTail[(*str - 0xAC00) % 28];
            pos+=3;
        } else {
            if (pos + 1 > nSize - 1)
                break;

            buffer[pos] = *str;
            ++pos;
        }
        ++str;
    }

    buffer[pos] = '\0';

    return pos;
}

// reference: http://cozyu-textcube.blogspot.com/2008/01/string-wstring-%EB%B3%80%ED%99%98.html
std::wstring mbs_to_wcs(const std::string& str, const std::locale& loc = std::locale("ko_KR.UTF-8"))
{
    typedef std::codecvt<wchar_t, char, std::mbstate_t> codecvt_t;
    const codecvt_t& codecvt = std::use_facet<codecvt_t>(loc);
    std::mbstate_t state = std::mbstate_t();
    std::vector<wchar_t> buf(str.size() + 1);
    const char* in_next = str.c_str();
    wchar_t* out_next = &buf[0];
    codecvt_t::result r = codecvt.in(state,
        str.c_str(), str.c_str() + str.size(), in_next,
        &buf[0], &buf[0] + buf.size(), out_next);

    return std::wstring(&buf[0]);
}

// reference: http://cozyu-textcube.blogspot.com/2008/01/string-wstring-%EB%B3%80%ED%99%98.html
std::string wcs_to_mbs(const std::wstring& str, const std::locale& loc = std::locale("ko_KR.UTF-8"))
{
    typedef std::codecvt<wchar_t, char, std::mbstate_t> codecvt_t;
    const codecvt_t& codecvt = std::use_facet<codecvt_t>(loc);
    std::mbstate_t state = std::mbstate_t();;
    std::vector<char> buf((str.size() + 1) * codecvt.max_length());
    const wchar_t* in_next = str.c_str();
    char* out_next = &buf[0];
    codecvt_t::result r = codecvt.out(state,
        str.c_str(), str.c_str() + str.size(), in_next,
        &buf[0], &buf[0] + buf.size(), out_next);
    return std::string(&buf[0]);
}

bool isHangulSyllable(const std::string& mbsLetter) {
    const std::wstring& wcsLetter = mbs_to_wcs(mbsLetter);
    const wchar_t* wcpChar = wcsLetter.c_str();
    return 0xAC00 <= *wcpChar && *wcpChar <= 0xD7A3;  // between '가' and '힣'
}

const wchar_t& getLastWStrChar(const std::string& mbsStr) {
    const std::wstring& wStr = mbs_to_wcs(mbsStr);
    return wStr[wStr.size() - 1];
}

int main(void) {
    std::locale::global(std::locale("ko_KR.UTF-8"));

    const wchar_t* tmpWchar = L"ㅋ";
    wprintf(L"%ls\n", tmpWchar);
    wprintf(L"%#x\n", *tmpWchar);

    std::string mbs_str1 = "__label__0 tv 전기세가 아깝다!!!ㅋㅋ-_-'(越不聰明越快活)any가";
    std::wstring wcs_str1 = mbs_to_wcs(mbs_str1);
    std::string mbs_str2 = wcs_to_mbs(wcs_str1);
    std::wstring wcs_str2 = mbs_to_wcs(mbs_str2);

    assert(mbs_str1 == mbs_str2);
    assert(wcs_str1 == wcs_str2);

    const wchar_t* str = wcs_str2.c_str();
    wprintf(L"[wcs_str2] %ls\n", str);
    std::cout << "[mbs_str2] " << mbs_str2 << std::endl;

    wchar_t buffer[4096];

    BreakHan(str, buffer, sizeof buffer);
    printf("(printf) %S\n", buffer);
    printf("(printf) %ls\n", buffer);
    wprintf(L"(wprintf) %S\n", buffer);  // both %ls & %S work the same
    wprintf(L"(wprintf) %ls\n", buffer);

    std::cout << std::endl << "[unicode code range test]" << std::endl;
    std::wstring wchr = mbs_to_wcs("ㅋ");
    str = wchr.c_str();
    wprintf(L"(char) %ls\n", str);
    printf("(code) %#x\n", *str);
    // reference: http://www.unicode.org/charts/PDF/U3130.pdf
    // (Hangul Compatibility Jamo unicode character code table)
    std::cout << (bool)(0x3131 <= *str && *str <= 0x318E) << std::endl;

    std::cout << std::endl << "[Hangul syllable test 1]" << std::endl;
    std::string letter = "뷁";
    std::cout <<"Is " << letter << " a korean letter? " << isHangulSyllable(letter) << std::endl;

    std::cout << std::endl << "[Hangul syllable test 2]" << std::endl;
    std::cout << "wcs_str2.size():" << wcs_str2.size() << std::endl;
    wprintf(L"wcs_str2: %ls\n", wcs_str2.c_str());
    std::cout << "(cout) wcs_str2 last character: " << wcs_str2[wcs_str2.size() - 1] << std::endl;
    wprintf(L"(wprintf) wcs_str2 last character: %ls(%#X)\n",
        &(wcs_str2[wcs_str2.size() - 1]), wcs_str2[wcs_str2.size() - 1]);
    std::cout << "0xAC00 <= getLastWStrChar(mbs_str1) && getLastWStrChar(mbs_str1) <= 0xD7A3: "
              << (0xAC00 <= getLastWStrChar(mbs_str1) && getLastWStrChar(mbs_str1)) << std::endl;

    return 0;
}

